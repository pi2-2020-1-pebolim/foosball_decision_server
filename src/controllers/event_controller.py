from utils.convert_base64 import Base64Convertion
from sklearn.linear_model import LinearRegression
from collections import deque
from flask import jsonify
from PIL import Image

import numpy as np
import imutils
import cv2 as cv
import io
import time

from model.field import Field
from model.ball import Ball
from controllers.image_controller import ImageController 
from controllers.decision_controller import DecisionController 

class EventController:

    def __init__(self, app, socketio):
       
        self.socketio = socketio
        self.app = app

        self.field = None
        self.ball = Ball()

        self.image_controller = ImageController(app, socketio, self)
        self.decision_controller = DecisionController(app, socketio, self) 


    def update_event(self, event):

        if self.field is None: 
            return
        
        # autocalibration for testing
        if not self.image_controller.is_calibrated:
            self.image_controller.calibrate_field(
                event['camera']['image']
            )

        # debug log
        # self.app.logger.info(self.image_controller.ROI)
        result = self.image_controller.process_image(event['camera']['image'])

        for lane_state in event['lanes']:
            for player in self.field.players_in_lane[lane_state['laneID']]:
                player.update_position(lane_state['currentPosition'])

        self.decision_controller.define_action()

        return result

    def register_event(self, event):
        
        if self.field is None:
            self.field = Field(
                lanes=event['fieldDefinition']['lanes'],
                dimensions=event['fieldDefinition']['dimensions'],
                resolution=event['cameraSettings']['resolution'],
                event_controller=self
            )

    def get_field(self):
        return self.field
