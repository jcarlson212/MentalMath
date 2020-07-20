import asyncio
import json
import random
from time import time 
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from .models import Thread, ChatMessage
from .models import User


MAX_NUM = 20
class FindGameConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("connected", event)
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        print("receive", event)
        print(event, " is trying to find a game")
        if not hasattr(self, 'userQ'):
            self.userQ = []
        self.userQ.append(event['text'])
        print(self.userQ)
        if(len(self.userQ) > 1):
            user1 = self.userQ.pop()
            user2 = self.userQ.pop()
            await self.send({
                "type": "websocket.message",
                "text": "/MentalMathWebsite/" + user1 + "/" + user2
            })
        else:
            #wait a bit before removing them from the queue and setting them up in a match against a bot
            await asyncio.sleep(5)
            userFound = False
            for i in range(0, len(self.userQ)):
                if self.userQ[i] == event['text']:
                    #remove it 
                    userFound = True
                    break
            if userFound:
                await self.send({
                    "type": "websocket.send",
                    "text": "/MentalMathWebsite/" + self.userQ.pop()
                })


    async def websocket_disconnect(self, event):
        print("disconnected", event)


class SoloGameConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        await self.send({
            "type": "websocket.accept"
        })
        postedString = "numbers posted:"
        operators = ["+", "*", "/", "-"]
        
        num1 = random.randint(1, MAX_NUM)
        
        op = operators[random.randint(0, len(operators)-1)]
        num2 = random.randint(1, MAX_NUM)
        self.num1 = num1
        self.op = op
        self.num2 = num2 
        self.count = 1
        diff = random.randint(2, 10)
        self.submissionTime = time() + diff

        prevCount = self.count
        await self.send({
            "type": "websocket.send",
            "text": postedString + " " + str(num1) + " " + op + " " + str(num2) + " " + str(diff),
        })

            

    async def newProblem(self):
        postedString = "numbers posted:"
        operators = ["+", "*", "/", "-"]
        num1 = random.randint(1, MAX_NUM)
        
        op = operators[random.randint(0, len(operators)-1)]
        num2 = random.randint(1, MAX_NUM)
        self.num1 = num1
        self.op = op
        self.num2 = num2 
        self.count = self.count + 1
        diff = random.randint(2, 10)
        self.submissionTime = time() + diff
    
        prevCount = self.count 
        await self.send({
            "type": "websocket.send",
            "text": postedString + " " + str(num1) + " " + op + " " + str(num2) + " " + str(diff),
        })

    async def websocket_receive(self, event):
        print(event, " was sent to us")
        startText = "start_new_game"
        endIndex = 0
        if event["text"][0] != ' ':
            while event["text"][endIndex + 1] != ' ':
                endIndex = endIndex + 1
        else:
            endIndex = -1

        if event["text"][0:endIndex+1] == "start_new_game":
            await self.newProblem()
        else:
            number_sent = int(event["text"][0:endIndex+1])
            person_sent = event["text"][endIndex+2:len(event["text"])]
            
            if self.submissionTime > time():
                if self.op == "+":
                    if self.num1 + self.num2 == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent)
                        await self.send({
                            "type": "websocket.send",
                            "text": "You won"
                        })
                elif self.op == "-":
                    if self.num1 - self.num2 == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent)
                        await self.send({
                            "type": "websocket.send",
                            "text": "You won"
                        })
                elif self.op == "/":
                    if int(self.num1 / self.num2) == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent)
                        await self.send({
                            "type": "websocket.send",
                            "text": "You won"
                        })
                elif self.op == "*":
                    if self.num1*self.num2 == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent)
                        await self.send({
                            "type": "websocket.send",
                            "text": "You won"
                        })
            else:
                await self.send({
                    "type": "websocket.send",
                    "text": "You lost"
                })



    async def websocket_disconnect(self, event):
        print("disconnected", event)

    @database_sync_to_async
    def add_point_to_user(self, username):
        winner = User.objects.get(username=username)
        winner.points = winner.points + 1
        winner.save()
        

class GameConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        await self.send({
            "type": "websocket.accept"
        })
        postedString = "numbers posted:"
        operators = ["+", "*", "/", "-"]
        
        num1 = random.randint(1, MAX_NUM)
        
        op = operators[random.randint(0, len(operators)-1)]
        num2 = random.randint(1, MAX_NUM)
        self.num1 = num1
        self.op = op
        self.num2 = num2 
        self.count = 1
        self.Q = []
        diff = 10
        self.submissionTime = time() + diff

        prevCount = self.count
        await self.send({
            "type": "websocket.send",
            "text": postedString + " " + str(num1) + " " + op + " " + str(num2) + " " + str(diff),
        })

            

    async def newProblem(self):
        postedString = "numbers posted:"
        operators = ["+", "*", "/", "-"]
        num1 = random.randint(1, MAX_NUM)
        
        op = operators[random.randint(0, len(operators)-1)]
        num2 = random.randint(1, MAX_NUM)
        self.num1 = num1
        self.op = op
        self.num2 = num2 
        self.Q = []
        self.count = self.count + 1
        diff = 10
        self.submissionTime = time() + diff
    
        prevCount = self.count 
        await self.send({
            "type": "websocket.send",
            "text": postedString + " " + str(num1) + " " + op + " " + str(num2) + " " + str(diff),
        })

    async def websocket_receive(self, event):
        print(event, " was sent to us")
        startText = "start_new_game"
        endIndex = 0
        if event["text"][0] != ' ':
            while event["text"][endIndex + 1] != ' ':
                endIndex = endIndex + 1
        else:
            endIndex = -1

        if event["text"][0:endIndex+1] == "start_new_game":
            await self.newProblem()
        else:
            number_sent = int(event["text"][0:endIndex+1])
            person_sent = event["text"][endIndex+2:len(event["text"])]
            if self.submissionTime > time():
                if self.op == "+":
                    if self.num1 + self.num2 == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent)
                        await self.send({
                            "type": "websocket.send",
                            "text": person_sent + " won"
                        })
                elif self.op == "-":
                    if self.num1 - self.num2 == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent)
                        await self.send({
                            "type": "websocket.send",
                            "text": person_sent + " won"
                        })
                elif self.op == "/":
                    if int(self.num1 / self.num2) == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent)
                        await self.send({
                            "type": "websocket.send",
                            "text": person_sent + " won"
                        })
                elif self.op == "*":
                    if self.num1*self.num2 == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent)
                        await self.send({
                            "type": "websocket.send",
                            "text": person_sent + " won"
                        })
            else:
                await self.send({
                    "type": "websocket.send",
                    "text": "You lost"
                })



    async def websocket_disconnect(self, event):
        print("disconnected", event)

    @database_sync_to_async
    def add_point_to_user(self, username):
        winner = User.objects.get(username=username)
        winner.points = winner.points + 1
        winner.save()

class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        await self.send({
            "type": "websocket.accept"
        })
        print("url rout: ")
        print(self.scope['url_route'])
        #other_user = self.scope['url_route']['kwargs']['username']
        #me = self.scope['user']
        #print(me, other_user)
       

    async def websocket_receive(self, event):
        print("receive", event)

    async def websocket_disconnect(self, event):
        print("disconnected", event)

    @database_sync_to_async
    def get_thread(self, user, other_username):
        return Tread.objects.get_or_new(user, other_username)[0]