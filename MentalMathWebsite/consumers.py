import asyncio
import json
import random
import threading
from time import time, sleep
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync

from .models import User, Submission

MAX_NUM = 20


userQ = []
matches = {
    #route -> { user1: , user2: , isPaused: , num1: ,num2: , op:, submissionStartTime:, pauseCount: }
    
}

class FindGameConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("connected", event)
        print("URL ROUTE", self.scope["path"])
        await self.send({
            "type": "websocket.accept"
        })
        self.event_loop = asyncio.get_event_loop()
    
    async def websocket_error(self, event):
        print("error", event)

    async def websocket_receive(self, event):
        print("receive", event)
        print(event, " is trying to find a game")
        
        userQ.append(event['text'])
        print(userQ)
        if(len(userQ) > 1):
            user1 = userQ.pop()
            user2 = userQ.pop()
            print("sending")
            route = "/MentalMathWebsite/" + user1 + "/" + user2
            operators = ["+", "*", "/", "-"]
            matches[route] = {
                "user1": user1,
                "user2": user2,
                "isPaused": False,
                "num1": random.randint(1, MAX_NUM),
                "num2":random.randint(1, MAX_NUM),
                "submissionStartTime": time(),
                "op": operators[random.randint(0, len(operators)-1)],
                "pauseCount": 0
            }
            await self.send({
                "type": "websocket.send",
                "text": "/MentalMathWebsite/" + user1 + "/" + user2
            })
            print("sent")
        else:
            #wait a bit before removing them from the queue and setting them up in a match against a bot
            await self.determine_match(event["text"])

    @database_sync_to_async
    def determine_match(self, username):
        vs_ai_thread = threading.Thread(
            target=self.determine_if_user_vs_ai, 
            args=(username,)
        )
        vs_ai_thread.start()

    async def give_user_ai_match(self, username):
        print("sending ai match")
        await self.send({
            "type": "websocket.send",
            "text": "/MentalMathWebsite/" + username
        })
        print("ai match sent")

    def determine_if_user_vs_ai(self, username):
        print("about to sleep", time())
        for i in range(0, 10):
            sleep(.5)
            for key in matches:
                if matches[key]["user1"] == username or matches[key]["user2"] == username:
                    asyncio.ensure_future(self.give_user_match(key), loop=self.event_loop)
                    return
        
        userFound = False
        print("finished sleeping", time())
        print(userQ)
        for i in range(0, len(userQ)):
            if userQ[i] == username:
                #remove it 
                userFound = True
                break
        if userFound:
            userQ.remove(username)
            print("starting ai match")
            asyncio.ensure_future(self.give_user_ai_match(username), loop=self.event_loop)
        else:
            #they need to be added to a match with another player
            for key in matches:
                if matches[key]["user1"] == username or matches[key]["user2"] == username:
                    asyncio.ensure_future(self.give_user_match(key), loop=self.event_loop)
                    break
    
    async def give_user_match(self, route):
        await self.send({
            "type": "websocket.send",
            "text": route
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
        print("USERNAME FOR DATABASE REQUEST: ",username)
        user = User.objects.get(username=username)
        submission = Submission(
            user=user,
            againstAI=againstAI,
            isCorrect=isCorrect,
            typeOfProblem=op,
            timeToFinish=timeTaken
        )
        submission.save()
        
class GameConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        await self.send({
            "type": "websocket.accept"
        })
        postedString = "numbers posted:"
        self.match_route = self.scope["path"]
        num1 = matches[self.match_route]["num1"]
        num2 = matches[self.match_route]["num2"]
        op = matches[self.match_route]["op"]


        await self.send({
            "type": "websocket.send",
            "text": postedString + " " + str(num1) + " " + op + " " + str(num2),
        })

            

    async def newProblem(self):
        try:
            while matches[self.match_route]["pauseCount"] < 2 and matches[self.match_route]["isPaused"]:
                await asyncio.sleep(.1)
            matches[self.match_route]["pauseCount"] = 0
            matches[self.match_route]["isPaused"] = False
            postedString = "numbers posted:"
            self.match_route = self.scope["path"]
            num1 = matches[self.match_route]["num1"]
            num2 = matches[self.match_route]["num2"]
            op = matches[self.match_route]["op"]
            await self.send({
                "type": "websocket.send",
                "text": postedString + " " + str(num1) + " " + op + " " + str(num2),
            })
        except:
            print("exception occurred")

    async def websocket_receive(self, event):
        print(event, " was sent to us")
        startText = "start_new_game"
        endIndex = 0
        try:
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
                if not matches[self.match_route]["isPaused"]:
                    if matches[self.match_route]["op"] == "+":
                        if matches[self.match_route]["num1"] + matches[self.match_route]["num2"] == number_sent and not matches[self.match_route]["isPaused"]:
                            matches[self.match_route]["isPaused"] = True
                            matches[self.match_route]["pauseCount"] = 1
                            await self.add_point_to_user(person_sent, matches[self.match_route]["op"])
                            await self.add_submission(
                                username=person_sent,
                                op=matches[self.match_route]["op"],
                                timeTaken=(time() - matches[self.match_route]["submissionStartTime"]),
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
                                timeTaken=(time() - matches[self.match_route]["submissionStartTime"]),
                                againstAI=True,
                                isCorrect=False
                            )
                            operators = ["+", "*", "/", "-"]
                            num1 = random.randint(1, MAX_NUM)
                            op = operators[random.randint(0, len(operators)-1)]
                            num2 = random.randint(1, MAX_NUM)
                            matches[self.match_route]["num1"] = num1
                            matches[self.match_route]["op"] = op
                            matches[self.match_route]["num2"] = num2 
                            matches[self.match_route]["submissionStartTime"] = time()
                            matches[self.match_route]["pauseCount"] = 2
                            await self.send({
                                "type": "websocket.send",
                                "text": "You lost"
                            })

                    elif matches[self.match_route]["op"] == "-":
                        if matches[self.match_route]["num1"] - matches[self.match_route]["num2"] == number_sent and not matches[self.match_route]["isPaused"]:
                            matches[self.match_route]["isPaused"] = True
                            matches[self.match_route]["pauseCount"] = 1
                            await self.add_point_to_user(person_sent, matches[self.match_route]["op"])
                            await self.add_submission(
                                username=person_sent,
                                op=matches[self.match_route]["op"],
                                timeTaken=(time() - matches[self.match_route]["submissionStartTime"]),
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
                                op=matches[self.match_route]["op"],
                                timeTaken=(time() - matches[self.match_route]["submissionStartTime"]),
                                againstAI=True,
                                isCorrect=False
                            )
                            operators = ["+", "*", "/", "-"]
                            num1 = random.randint(1, MAX_NUM)
                            op = operators[random.randint(0, len(operators)-1)]
                            num2 = random.randint(1, MAX_NUM)
                            matches[self.match_route]["num1"] = num1
                            matches[self.match_route]["op"] = op
                            matches[self.match_route]["num2"] = num2 
                            matches[self.match_route]["submissionStartTime"] = time()
                            matches[self.match_route]["pauseCount"] = 2
                            await self.send({
                                "type": "websocket.send",
                                "text": "You lost"
                            })
                    elif matches[self.match_route]["op"] == "/":
                        if int(matches[self.match_route]["num1"] / matches[self.match_route]["num2"]) == number_sent and not matches[self.match_route]["isPaused"]:
                            matches[self.match_route]["isPaused"] = True
                            matches[self.match_route]["pauseCount"] = 1
                            await self.add_point_to_user(person_sent, matches[self.match_route]["op"])
                            await self.add_submission(
                                username=person_sent,
                                op=matches[self.match_route]["op"],
                                timeTaken=(time() - matches[self.match_route]["submissionStartTime"]),
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
                                op=matches[self.match_route]["op"],
                                timeTaken=(time() - matches[self.match_route]["submissionStartTime"]),
                                againstAI=True,
                                isCorrect=False
                            )
                            operators = ["+", "*", "/", "-"]
                            num1 = random.randint(1, MAX_NUM)
                            op = operators[random.randint(0, len(operators)-1)]
                            num2 = random.randint(1, MAX_NUM)
                            matches[self.match_route]["num1"] = num1
                            matches[self.match_route]["op"] = op
                            matches[self.match_route]["num2"] = num2 
                            matches[self.match_route]["submissionStartTime"] = time()
                            matches[self.match_route]["pauseCount"] = 2
                            await self.send({
                                "type": "websocket.send",
                                "text": "You lost"
                            })
                    elif matches[self.match_route]["op"] == "*":
                        if matches[self.match_route]["num1"]*matches[self.match_route]["num2"] == number_sent and not matches[self.match_route]["isPaused"]:
                            matches[self.match_route]["isPaused"] = True
                            matches[self.match_route]["pauseCount"] = 1
                            await self.add_point_to_user(person_sent, matches[self.match_route]["op"])
                            await self.add_submission(
                                username=person_sent,
                                op=matches[self.match_route]["op"],
                                timeTaken=(time() - matches[self.match_route]["submissionStartTime"]),
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
                                op=matches[self.match_route]["op"],
                                timeTaken=(time() - matches[self.match_route]["submissionStartTime"]),
                                againstAI=True,
                                isCorrect=False
                            )
                            operators = ["+", "*", "/", "-"]
                            num1 = random.randint(1, MAX_NUM)
                            op = operators[random.randint(0, len(operators)-1)]
                            num2 = random.randint(1, MAX_NUM)
                            matches[self.match_route]["num1"] = num1
                            matches[self.match_route]["op"] = op
                            matches[self.match_route]["num2"] = num2 
                            matches[self.match_route]["submissionStartTime"] = time()
                            matches[self.match_route]["pauseCount"] = 2
                            await self.send({
                                "type": "websocket.send",
                                "text": "You lost"
                            })
                else:
                    await self.add_submission(
                        username=person_sent,
                        op=matches[self.match_route]["op"],
                        timeTaken=(time() - matches[self.match_route]["submissionStartTime"]),
                        againstAI=True,
                        isCorrect=False
                    )
                    operators = ["+", "*", "/", "-"]
                    num1 = random.randint(1, MAX_NUM)
                    op = operators[random.randint(0, len(operators)-1)]
                    num2 = random.randint(1, MAX_NUM)
                    matches[self.match_route]["num1"] = num1
                    matches[self.match_route]["op"] = op
                    matches[self.match_route]["num2"] = num2 
                    matches[self.match_route]["submissionStartTime"] = time()
                    matches[self.match_route]["pauseCount"] = 2
                    matches[self.match_route]["pauseCount"] = 2
                    await self.send({
                        "type": "websocket.send",
                        "text": "You lost"
                    })
        except:
            print("exception occurred")



    async def websocket_disconnect(self, event):
        print("disconnected", event)
        matches.pop(self.match_route)

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
