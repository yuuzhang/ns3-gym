import zmq
import sys

import numpy as np

import gym
from gym import spaces
from gym.utils import seeding
from enum import IntEnum

import messages_pb2 as pb
from google.protobuf.any_pb2 import Any


__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2018, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class Ns3ZmqBridge(object):
    """docstring for Ns3ZmqBridge"""
    def __init__(self, port="5555"):
        super(Ns3ZmqBridge, self).__init__()
        self.port = port
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect ("tcp://localhost:%s" % port)

    def send_init_request(self, stepInterval):
        # print ("Sending INIT request ")
        msg = pb.InitializeRequest()
        msg.timeStep = stepInterval

        requestMsg = pb.RequestMsg()
        requestMsg.type = pb.Init
        requestMsg.msg.Pack(msg)
        requestMsg = requestMsg.SerializeToString()

        self.socket.send(requestMsg)
        reply = self.socket.recv()
        replyPbMsg = pb.ReplyMsg()
        initReplyPbMsg = pb.InitializeReply()
        replyPbMsg.ParseFromString(reply)
        replyPbMsg.msg.Unpack(initReplyPbMsg)
        errCode = 0
        value = int(initReplyPbMsg.done)
        return [errCode, value]

    def initialize_env(self, stepInterval):
        [errCode, value] = self.send_init_request(stepInterval)
        return value

    def _create_space(self, spaceReplyPb):
        space = None
        if (spaceReplyPb.type == pb.Discrete):
            discreteSpacePb = pb.DiscreteSpace()
            spaceReplyPb.space.Unpack(discreteSpacePb)
            space = spaces.Discrete(discreteSpacePb.n)

        elif (spaceReplyPb.type == pb.Box):
            boxSpacePb = pb.BoxSpace()
            spaceReplyPb.space.Unpack(boxSpacePb)
            low = boxSpacePb.low
            high = boxSpacePb.high
            shape = tuple(boxSpacePb.shape)
            mtype = boxSpacePb.dtype

            if mtype == pb.INT:
                mtype = np.int
            elif mtype == pb.UINT:
                mtype = np.uint
            elif mtype == pb.DOUBLE:
                mtype = np.float
            else:
                mtype = np.float

            space = spaces.Box(low=low, high=high, shape=shape, dtype=mtype)
        return space

    def send_get_action_space_request(self):
        msg = pb.GetActionSpaceRequest()
        requestMsg = pb.RequestMsg()
        requestMsg.type = pb.ActionSpace
        requestMsg.msg.Pack(msg)
        requestMsg = requestMsg.SerializeToString()
        self.socket.send(requestMsg)

        reply = self.socket.recv()
        replyPbMsg = pb.ReplyMsg()
        actionApaceReplyPbMsg = pb.GetSpaceReply()
        replyPbMsg.ParseFromString(reply)
        replyPbMsg.msg.Unpack(actionApaceReplyPbMsg)
        return actionApaceReplyPbMsg

    def get_action_space(self):
        spaceReplyPb = self.send_get_action_space_request()
        actionSpace = self._create_space(spaceReplyPb)
        return actionSpace

    def send_get_obs_space_request(self):
        msg = pb.GetObservationSpaceRequest()
        requestMsg = pb.RequestMsg()
        requestMsg.type = pb.ObservationSpace
        requestMsg.msg.Pack(msg)
        requestMsg = requestMsg.SerializeToString()
        self.socket.send(requestMsg)

        reply = self.socket.recv()
        replyPbMsg = pb.ReplyMsg()
        obsApaceReplyPbMsg = pb.GetSpaceReply()
        replyPbMsg.ParseFromString(reply)
        replyPbMsg.msg.Unpack(obsApaceReplyPbMsg)
        return obsApaceReplyPbMsg

    def get_observation_space(self):
        spaceReplyPb = self.send_get_obs_space_request()
        obsSpace = self._create_space(spaceReplyPb)        
        return obsSpace

    def send_is_game_over_request(self):
        msg = pb.GetIsGameOverRequest()
        requestMsg = pb.RequestMsg()
        requestMsg.type = pb.IsGameOver
        requestMsg.msg.Pack(msg)
        requestMsg = requestMsg.SerializeToString()
        self.socket.send(requestMsg)

        reply = self.socket.recv()
        replyPbMsg = pb.ReplyMsg()
        innerReplyPbMsg = pb.GetIsGameOverReply()
        replyPbMsg.ParseFromString(reply)
        replyPbMsg.msg.Unpack(innerReplyPbMsg)
        return innerReplyPbMsg

    def is_game_over(self):
        msg = self.send_is_game_over_request()
        return msg.isGameOver

    def send_get_state_request(self):
        msg = pb.GetObservationRequest()
        requestMsg = pb.RequestMsg()
        requestMsg.type = pb.Observation
        requestMsg.msg.Pack(msg)
        requestMsg = requestMsg.SerializeToString()
        self.socket.send(requestMsg)

        reply = self.socket.recv()
        replyPbMsg = pb.ReplyMsg()
        innerReplyPbMsg = pb.GetObservationReply()
        replyPbMsg.ParseFromString(reply)
        replyPbMsg.msg.Unpack(innerReplyPbMsg)
        return innerReplyPbMsg

    def get_obs(self):
        obsMsg = self.send_get_state_request()
        dataContainer = obsMsg.container

        data = None
        if (dataContainer.type == pb.Box):
            boxContainerPb = pb.BoxDataContainer()
            dataContainer.data.Unpack(boxContainerPb)
            # print(boxContainerPb.shape, boxContainerPb.dtype, boxContainerPb.uintData)

            if boxContainerPb.dtype == pb.INT:
                data = boxContainerPb.intData
            elif boxContainerPb.dtype == pb.UINT:
                data = boxContainerPb.uintData
            elif boxContainerPb.dtype == pb.DOUBLE:
                data = boxContainerPb.doubleData
            else:
                data = boxContainerPb.floatData

            # TODO: reshape using shape info

        return data

    def send_get_reward_request(self):
        msg = pb.GetRewardRequest()
        requestMsg = pb.RequestMsg()
        requestMsg.type = pb.Reward
        requestMsg.msg.Pack(msg)
        requestMsg = requestMsg.SerializeToString()
        self.socket.send(requestMsg)

        reply = self.socket.recv()
        replyPbMsg = pb.ReplyMsg()
        innerReplyPbMsg = pb.GetRewardReply()
        replyPbMsg.ParseFromString(reply)
        replyPbMsg.msg.Unpack(innerReplyPbMsg)
        return innerReplyPbMsg

    def get_reward(self):
        rewardMsg = self.send_get_reward_request()
        return rewardMsg.reward

    def send_execute_action_request(self, actions):
        dataContainer = pb.DataContainer()
        dataContainer.type = pb.Box
        
        boxContainerPb = pb.BoxDataContainer()
        boxContainerPb.dtype = pb.UINT
        #TODO: shape correctly using numpy
        shape = [len(actions)]
        boxContainerPb.shape.extend(shape)
        boxContainerPb.uintData.extend(actions)
        dataContainer.data.Pack(boxContainerPb)

        msg = pb.SetActionRequest()
        msg.container.CopyFrom(dataContainer) 

        requestMsg = pb.RequestMsg()
        requestMsg.type = pb.Action
        requestMsg.msg.Pack(msg)
        requestMsg = requestMsg.SerializeToString()
        self.socket.send(requestMsg)

        reply = self.socket.recv()
        replyPbMsg = pb.ReplyMsg()
        innerReplyPbMsg = pb.SetActionReply()
        replyPbMsg.ParseFromString(reply)
        replyPbMsg.msg.Unpack(innerReplyPbMsg)
        return innerReplyPbMsg

    def execute_action(self, actions):
        replyMsg = self.send_execute_action_request(actions)
        return replyMsg.done


class Ns3Env(gym.Env):
    def __init__(self, stepTime):
        self.stepTime = stepTime
        self.port = "5555"

        # TODO: start ns3 script from here
        self.ns3ZmqBridge = Ns3ZmqBridge(self.port)
        self.ns3ZmqBridge.initialize_env(stepTime)
        self.action_space = self.ns3ZmqBridge.get_action_space()
        self.observation_space = self.ns3ZmqBridge.get_observation_space()

        self._seed()
        self.viewer = None
        self.state = None
        self.steps_beyond_done = None

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _get_obs(self):
        done = self.ns3ZmqBridge.is_game_over()
        obs = self.ns3ZmqBridge.get_obs()
        reward = self.ns3ZmqBridge.get_reward()
        return (obs, reward, done, {})

    def step(self, action):
        response = self.ns3ZmqBridge.execute_action(action)
        return self._get_obs()

    def reset(self):
        # TODO: add reset function
        return self._get_obs()

    def render(self, mode='human'):
        return

    def get_random_action(self):
        act = self.action_space.sample()
        return act

    def close(self):
        if self.viewer:
            self.viewer.close()