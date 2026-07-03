from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone


STAFF_INBOX_GROUP = 'staff_inbox'


class StaffInboxConsumer(AsyncJsonWebsocketConsumer):
    """Lightweight consumer for the staff messages list page.
    Receives new_message events to update room previews in real time."""

    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous or not (user.is_staff or user.is_advisor):
            await self.close()
            return
        await self.channel_layer.group_add(STAFF_INBOX_GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(STAFF_INBOX_GROUP, self.channel_name)

    async def inbox_message(self, event):
        await self.send_json({
            'type': 'inbox_message',
            'room_id': event['room_id'],
            'sender_name': event['sender_name'],
            'is_staff': event['is_staff'],
            'content': event['content'],
            'timestamp': event['timestamp'],
        })


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.group_name = f'chat_{self.room_id}'
        user = self.scope['user']

        if user.is_anonymous:
            await self.close()
            return

        has_access = await self._check_access(user, self.room_id)
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Mark existing messages as seen on connect
        count = await self._mark_messages_seen(user, self.room_id)
        if count:
            await self.channel_layer.group_send(self.group_name, {
                'type': 'messages_seen',
                'seen_by': user.id,
                'room_id': self.room_id,
            })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        action = content.get('action')
        user = self.scope['user']

        if action == 'message':
            text = (content.get('message') or '').strip()
            if not text:
                return
            msg_data = await self._save_message(
                user,
                self.room_id,
                text,
                content.get('reply_to'),
            )
            await self.channel_layer.group_send(self.group_name, {
                'type': 'chat_message',
                **msg_data,
            })
            await self._notify_for_new_message(
                user=user,
                room_id=self.room_id,
                message_id=msg_data['id'],
                preview=msg_data['content'],
            )
            # Notify staff inbox list
            await self.channel_layer.group_send(STAFF_INBOX_GROUP, {
                'type': 'inbox_message',
                'room_id': int(self.room_id),
                'sender_name': msg_data['sender_name'],
                'is_staff': msg_data['is_staff'],
                'content': msg_data['content'],
                'timestamp': msg_data['timestamp'],
            })

        elif action == 'edit_message':
            text = (content.get('message') or '').strip()
            if not text:
                return
            edit_data = await self._edit_message(
                user,
                self.room_id,
                content.get('message_id'),
                text,
            )
            if not edit_data:
                return

            await self.channel_layer.group_send(self.group_name, {
                'type': 'message_edited',
                **edit_data,
            })

            if edit_data['is_last']:
                await self.channel_layer.group_send(STAFF_INBOX_GROUP, {
                    'type': 'inbox_message',
                    'room_id': int(self.room_id),
                    'sender_name': edit_data['sender_name'],
                    'is_staff': edit_data['is_staff'],
                    'content': edit_data['content'],
                    'timestamp': edit_data['timestamp'],
                })

        elif action == 'mark_seen':
            count = await self._mark_messages_seen(user, self.room_id)
            if count:
                await self.channel_layer.group_send(self.group_name, {
                    'type': 'messages_seen',
                    'seen_by': user.id,
                    'room_id': self.room_id,
                })

    # ── Group event handlers ──

    async def chat_message(self, event):
        await self.send_json({
            'type': 'chat_message',
            'id': event['id'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'is_staff': event['is_staff'],
            'content': event['content'],
            'timestamp': event['timestamp'],
            'status': event['status'],
            'reply_to_id': event['reply_to_id'],
            'reply_to_content': event['reply_to_content'],
            'reply_to_sender_name': event['reply_to_sender_name'],
            'edited': event['edited'],
        })

    async def message_edited(self, event):
        await self.send_json({
            'type': 'message_edited',
            'id': event['id'],
            'sender_id': event['sender_id'],
            'content': event['content'],
            'edited_at': event['edited_at'],
            'timestamp': event['timestamp'],
        })

    async def messages_seen(self, event):
        await self.send_json({
            'type': 'messages_seen',
            'seen_by': event['seen_by'],
            'room_id': event['room_id'],
        })

    # ── DB helpers ──

    @database_sync_to_async
    def _check_access(self, user, room_id):
        from apps.chat.models import ChatRoom
        try:
            room = ChatRoom.objects.get(pk=room_id)
        except ChatRoom.DoesNotExist:
            return False
        return room.student_id == user.id or user.is_staff or user.is_advisor

    @database_sync_to_async
    def _save_message(self, user, room_id, text, reply_to_id=None):
        from apps.chat.models import Message
        reply_to = None
        if reply_to_id:
            try:
                reply_to = Message.objects.select_related('sender').get(
                    pk=int(reply_to_id),
                    room_id=room_id,
                )
            except (ValueError, TypeError, Message.DoesNotExist):
                reply_to = None

        msg = Message.objects.create(
            room_id=room_id,
            sender=user,
            content=text,
            reply_to=reply_to,
            status='sent',
        )
        return self._serialize_message(msg)

    @database_sync_to_async
    def _notify_for_new_message(self, user, room_id, message_id, preview):
        from apps.chat.models import ChatRoom
        from apps.notifications.services import dispatch_notification, notify_staff

        try:
            room = ChatRoom.objects.select_related('student').get(pk=room_id)
        except ChatRoom.DoesNotExist:
            return
        if user.is_staff or user.is_advisor:
            dispatch_notification(
                user=room.student,
                created_by=user,
                audience='student',
                notification_type='new_message',
                category='chat',
                priority='normal',
                title='Nouveau message du conseiller',
                message=preview or 'Vous avez recu un nouveau message.',
                link='/dashboard/messages/',
                payload={'room_id': int(room_id), 'message_id': message_id},
            )
            return

        notify_staff(
            created_by=user,
            notification_type='staff_new_message',
            category='chat',
            priority='normal',
            title='Nouveau message etudiant',
            message=f'{user.email} a envoye un message.',
            link=f'/messages/{int(room_id)}/',
            payload={'student_id': user.id, 'room_id': int(room_id), 'message_id': message_id},
        )

    @database_sync_to_async
    def _edit_message(self, user, room_id, message_id, text):
        from apps.chat.models import Message
        try:
            message_id = int(message_id)
        except (ValueError, TypeError):
            return None

        msg = Message.objects.select_related('sender').filter(
            pk=message_id,
            room_id=room_id,
            sender_id=user.id,
        ).first()
        if not msg:
            return None

        msg.content = text
        msg.edited_at = timezone.now()
        msg.save(update_fields=['content', 'edited_at'])

        latest_id = Message.objects.filter(room_id=room_id).order_by('-created_at', '-id').values_list('id', flat=True).first()
        return {
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_name': msg.sender.first_name or msg.sender.email.split('@')[0],
            'is_staff': bool(msg.sender.is_staff or msg.sender.is_advisor),
            'content': msg.content,
            'edited_at': msg.edited_at.strftime('%H:%M'),
            'timestamp': msg.created_at.strftime('%H:%M'),
            'is_last': latest_id == msg.id,
        }

    @database_sync_to_async
    def _mark_messages_seen(self, user, room_id):
        from apps.chat.models import Message
        now = timezone.now()
        return Message.objects.filter(
            room_id=room_id,
            status='sent',
        ).exclude(
            sender=user,
        ).update(status='seen', seen_at=now)

    def _serialize_message(self, msg):
        reply = msg.reply_to
        reply_preview = ''
        if reply:
            reply_preview = (reply.content or '').strip()
            if not reply_preview and reply.file:
                reply_preview = 'Piece jointe'
        return {
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_name': msg.sender.first_name or msg.sender.email.split('@')[0],
            'is_staff': bool(msg.sender.is_staff or msg.sender.is_advisor),
            'content': msg.content,
            'timestamp': msg.created_at.strftime('%H:%M'),
            'status': msg.status,
            'reply_to_id': reply.id if reply else None,
            'reply_to_content': reply_preview,
            'reply_to_sender_name': (reply.sender.first_name or reply.sender.email.split('@')[0]) if reply else '',
            'edited': bool(msg.edited_at),
        }
