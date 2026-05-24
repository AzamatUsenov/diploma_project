import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import LiveSession


class LiveCodingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group = f'live_session_{self.session_id}'

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

        session = await self.get_session()
        if session:
            await self.send(text_data=json.dumps({
                'type': 'session_state',
                'status': session.status,
                'code': session.candidate_code,
                'current_question_index': session.current_question_index,
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')

        if msg_type == 'code_update':
            code = data.get('code', '')
            await self.save_code(code)
            await self.channel_layer.group_send(self.room_group, {
                'type': 'code_broadcast',
                'code': code,
                'sender_channel': self.channel_name,
            })

        elif msg_type == 'cursor_position':
            await self.channel_layer.group_send(self.room_group, {
                'type': 'cursor_broadcast',
                'line': data.get('line', 0),
                'col': data.get('col', 0),
                'sender_channel': self.channel_name,
            })

        elif msg_type == 'switch_task':
            index = data.get('index', 0)
            await self.save_question_index(index)
            await self.channel_layer.group_send(self.room_group, {
                'type': 'task_switch_broadcast',
                'index': index,
                'sender_channel': self.channel_name,
            })

        elif msg_type == 'run_result':
            await self.channel_layer.group_send(self.room_group, {
                'type': 'result_broadcast',
                'status': data.get('status'),
                'tests_passed': data.get('tests_passed', 0),
                'tests_total': data.get('tests_total', 0),
                'output': data.get('output', ''),
            })

        elif msg_type == 'chat_message':
            await self.channel_layer.group_send(self.room_group, {
                'type': 'chat_broadcast',
                'message': data.get('message', ''),
                'sender': data.get('sender', ''),
            })

        elif msg_type in ('webrtc_offer', 'webrtc_answer', 'webrtc_ice'):
            await self.channel_layer.group_send(self.room_group, {
                'type': 'webrtc_broadcast',
                'msg_type': msg_type,
                'payload': data.get('payload'),
                'sender_channel': self.channel_name,
            })

    async def code_broadcast(self, event):
        if event.get('sender_channel') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'code_update',
                'code': event['code'],
            }))

    async def cursor_broadcast(self, event):
        if event.get('sender_channel') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'cursor_position',
                'line': event['line'],
                'col': event['col'],
            }))

    async def task_switch_broadcast(self, event):
        if event.get('sender_channel') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'switch_task',
                'index': event['index'],
            }))

    async def result_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'run_result',
            'status': event['status'],
            'tests_passed': event['tests_passed'],
            'tests_total': event['tests_total'],
            'output': event['output'],
        }))

    async def chat_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
        }))

    async def extend_time_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'extend_time',
            'added': event['added'],
            'total_minutes': event['total_minutes'],
        }))

    async def webrtc_broadcast(self, event):
        if event.get('sender_channel') != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': event['msg_type'],
                'payload': event['payload'],
            }))

    @database_sync_to_async
    def get_session(self):
        try:
            return LiveSession.objects.get(id=self.session_id)
        except LiveSession.DoesNotExist:
            return None

    @database_sync_to_async
    def save_code(self, code):
        LiveSession.objects.filter(id=self.session_id).update(candidate_code=code)

    @database_sync_to_async
    def save_question_index(self, index):
        LiveSession.objects.filter(id=self.session_id).update(current_question_index=index)
