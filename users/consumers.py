import json
from .models import ChatTopic, ChatMessage
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.topic_id = self.scope['url_route']['kwargs']['topic_id']
        self.room_group_name = f'chat_{self.topic_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.set_user_online()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'is_online': True,
                'last_seen_text': 'online',
            }
        )

    async def disconnect(self, close_code):

        if not self.user.is_authenticated:
            return

        await self.set_user_offline()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'is_online': False,
                'last_seen_text': 'только что',
            }
        )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'delete_message':

            message_id = data.get('message_id')
            delete_for_all = data.get('delete_for_all', False)

            success = await self.delete_message(
                message_id,
                delete_for_all
            )

            if success:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': {
                            'type': 'message_deleted',
                            'message_id': message_id,
                            'delete_for_all': delete_for_all,
                        }
                    }
                )
            return
        if data.get('type') == 'edit_message':

            message_id = data.get('message_id')
            new_text = data.get('text', '').strip()

            updated = await self.edit_message(
                message_id,
                new_text
            )

            if updated:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': {
                            'type': 'message_edited',
                            'message_id': message_id,
                            'text': new_text,
                        }
                    }
                )

            return
        if data.get('type') == 'mark_read':

            await self.mark_messages_read()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'type': 'messages_read',
                        'user_id': self.user.id
                    }
                }
            )

            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': data
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'is_online': event['is_online'],
            'last_seen_text': event['last_seen_text'],
        }))

    @database_sync_to_async
    def set_user_online(self):
        self.user.last_activity = timezone.now()
        self.user.save(update_fields=['last_activity'])

    @database_sync_to_async
    def set_user_offline(self):
        self.user.last_activity = timezone.now()
        self.user.save(update_fields=['last_activity'])
   
    @database_sync_to_async
    def mark_messages_read(self):
        topic = ChatTopic.objects.get(id=self.topic_id)

        topic.messages.filter(
            is_read=False
        ).exclude(
            sender=self.user
        ).update(
            is_read=True
        )
    @database_sync_to_async
    def delete_message(self, message_id, delete_for_all=False):
        try:
            message = ChatMessage.objects.get(
                id=message_id,
                topic_id=self.topic_id,
                sender=self.user
            )
        except ChatMessage.DoesNotExist:
            return False

        if delete_for_all:
            message.delete()
            return True

        message.delete()
        return True    
    @database_sync_to_async
    def edit_message(self, message_id, new_text):
        if not new_text:
            return False

        try:
            message = ChatMessage.objects.get(
                id=message_id,
                topic_id=self.topic_id,
                sender=self.user,
                message_type='text'
            )
        except ChatMessage.DoesNotExist:
            return False

        message.text = new_text
        message.save(update_fields=['text'])

        return True
class PresenceConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.group_name = 'presence'

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.set_user_online()

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'is_online': True,
                'last_seen_text': 'online',
            }
        )

    async def disconnect(self, close_code):

        if not self.user.is_authenticated:
            return

        await self.set_user_offline()

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'is_online': False,
                'last_seen_text': 'только что',
            }
        )

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'is_online': event['is_online'],
            'last_seen_text': event['last_seen_text'],
        }))

    @database_sync_to_async
    def set_user_online(self):
        self.user.last_activity = timezone.now()
        self.user.save(update_fields=['last_activity'])

    @database_sync_to_async
    def set_user_offline(self):
        self.user.last_activity = timezone.now()
        self.user.save(update_fields=['last_activity'])        