import asyncio
import json
import random
import threading
from time import time, sleep
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from .models import User, Submission

MAX_NUM = 20
class FindGameConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("connected", event)
        await self.send({
            "type": "websocket.accept"
        })
        self.event_loop = asyncio.get_event_loop()

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
            await self.add_point_to_user(event["text"])

    @database_sync_to_async
    def add_point_to_user(self, username):
        vs_ai_thread = threading.Thread(
            target=self.determine_if_user_vs_ai, 
            args=(username,)
        )
        vs_ai_thread.start()

    async def give_user_ai_match(self, username):
        await self.send({
            "type": "websocket.send",
            "text": "/MentalMathWebsite/" + username
        })

    def determine_if_user_vs_ai(self, username):
        sleep(5)
        userFound = False
        for i in range(0, len(self.userQ)):
            if self.userQ[i] == username:
                #remove it 
                userFound = True
                break
        if userFound:
            print("Fdgfg")
            self.userQ.remove(username)
            asyncio.ensure_future(self.give_user_ai_match(username), loop=self.event_loop)
            

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
        self.submissionStartTime = time()
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
        self.submissionStartTime = time()
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
                        await self.add_point_to_user(person_sent, self.op)
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=True
                        )
                        await self.send({
                            "type": "websocket.send",
                            "text": "You won"
                        })
                    else:
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=False
                        )
                elif self.op == "-":
                    if self.num1 - self.num2 == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent, self.op)
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=True
                        )
                        await self.send({
                            "type": "websocket.send",
                            "text": "You won"
                        })
                    else:
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=False
                        )
                elif self.op == "/":
                    if int(self.num1 / self.num2) == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent, self.op)
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=True
                        )
                        await self.send({
                            "type": "websocket.send",
                            "text": "You won"
                        })
                    else:
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=False
                        )
                elif self.op == "*":
                    if self.num1*self.num2 == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent, self.op)
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=True
                        )
                        await self.send({
                            "type": "websocket.send",
                            "text": "You won"
                        })
                    else:
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=False
                        )
            else:
                await self.add_submission(
                    username=person_sent,
                    op=self.op,
                    timeTaken=(time() - self.submissionStartTime),
                    againstAI=True,
                    isCorrect=False
                )
                await self.send({
                    "type": "websocket.send",
                    "text": "You lost"
                })



    async def websocket_disconnect(self, event):
        print("disconnected", event)


    @database_sync_to_async
    def add_point_to_user(self, username, op):
        database_request_thread = threading.Thread(
            target=self.add_points_to_user_thread_func, 
            args=(username, op,)
        )
        database_request_thread.start()
        
    def add_points_to_user_thread_func(self, username, op):
        winner = User.objects.get(username=username)
        winner.points = winner.points + 1
        if op == "+":
            winner.addition = winner.addition + 1
        elif op == "-":
            winner.subtraction = winner.subtraction + 1
        elif op == "*":
            winner.multiplication = winner.multiplication + 1
        else:
            winner.division = winner.division + 1
        winner.save()

    @database_sync_to_async
    def add_submission(self, username, op, timeTaken, againstAI, isCorrect):
        database_request_thread = threading.Thread(
            target=self.add_submission_thread_func, 
            args=(username, op, timeTaken, againstAI, isCorrect,)
        )
        database_request_thread.start()
        
    def add_submission_thread_func(self, username, op, timeTaken, againstAI, isCorrect):
        user = User.objects.get(username=username)
        submission = Submission(
            user=user,
            againstAI=againstAI,
            isCorrect=isCorrect,
            typeOfProblem=op,
            timeToFinish=timeTaken
        )
        submission.save()
        


"""
    @database_sync_to_async
    def add_point_to_user(self, username):
        winner = User.objects.get(username=username)
        winner.points = winner.points + 1
        winner.save()
"""

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
        self.submissionStartTime = time()
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
        self.submissionStartTime = time()
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
                        await self.add_point_to_user(person_sent, self.op)
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=True
                        )
                        await self.send({
                            "type": "websocket.send",
                            "text": "You won"
                        })
                    else:
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=False
                        )
                elif self.op == "-":
                    if self.num1 - self.num2 == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent, self.op)
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=True
                        )
                        await self.send({
                            "type": "websocket.send",
                            "text": "You won"
                        })
                    else:
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=False
                        )
                elif self.op == "/":
                    if int(self.num1 / self.num2) == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent, self.op)
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=True
                        )
                        await self.send({
                            "type": "websocket.send",
                            "text": "You won"
                        })
                    else:
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=False
                        )
                elif self.op == "*":
                    if self.num1*self.num2 == number_sent:
                        self.paused = True
                        await self.add_point_to_user(person_sent, self.op)
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=True
                        )
                        await self.send({
                            "type": "websocket.send",
                            "text": "You won"
                        })
                    else:
                        await self.add_submission(
                            username=person_sent,
                            op=self.op,
                            timeTaken=(time() - self.submissionStartTime),
                            againstAI=True,
                            isCorrect=False
                        )
            else:
                await self.add_submission(
                    username=person_sent,
                    op=self.op,
                    timeTaken=(time() - self.submissionStartTime),
                    againstAI=True,
                    isCorrect=False
                )
                await self.send({
                    "type": "websocket.send",
                    "text": "You lost"
                })



    async def websocket_disconnect(self, event):
        print("disconnected", event)

    @database_sync_to_async
    def add_point_to_user(self, username, op):
        database_request_thread = threading.Thread(
            target=self.add_points_to_user_thread_func, 
            args=(username, op,)
        )
        database_request_thread.start()
        
    def add_points_to_user_thread_func(self, username, op):
        winner = User.objects.get(username=username)
        winner.points = winner.points + 1
        if op == "+":
            winner.addition = winner.addition + 1
        elif op == "-":
            winner.subtraction = winner.subtraction + 1
        elif op == "*":
            winner.multiplication = winner.multiplication + 1
        else:
            winner.division = winner.division + 1
        winner.save()


    @database_sync_to_async
    def add_submission(self, username, op, timeTaken, againstAI, isCorrect):
        database_request_thread = threading.Thread(
            target=self.add_submission_thread_func, 
            args=(username, op, timeTaken, againstAI, isCorrect,)
        )
        database_request_thread.start()
        
    def add_submission_thread_func(self, username, op, timeTaken, againstAI, isCorrect):
        user = User.objects.get(username=username)
        submission = Submission(
            user=user,
            againstAI=againstAI,
            isCorrect=isCorrect,
            typeOfProblem=op,
            timeToFinish=timeTaken
        )
        submission.save()
