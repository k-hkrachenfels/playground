from typing import Tuple
from attrs import define, field
from util.constant_set import ConstantSet
import numpy as np
from PIL import Image
import torch
import inspect

class Direction(ConstantSet):
    left='LEFT'
    right='RIGHT'
    up='UP'
    down='DOWN'

OPPOSITE_DIRECTION = {
    Direction.left: Direction.right,
    Direction.right: Direction.left,
    Direction.up: Direction.down,
    Direction.down: Direction.up
}

class Field(ConstantSet):
    right_upper = 'ru' # right upper quarter circle
    right_lower = 'rl' # right lower
    left_upper = 'lu' # left upper
    left_lower = 'll' # left lower
    horizontal  = 'h'  # horizontal line
    vertical  = 'v'  # vertical line
    empty  = 'e'  # empty field

field_images = {
    Field.horizontal: 'tiles/h.png',
    Field.vertical: 'tiles/v.png',
    Field.left_upper: 'tiles/lu.png',
    Field.right_upper :'tiles/ru.png',
    Field.right_lower: 'tiles/rl.png',
    Field.left_lower: 'tiles/ll.png',
    Field.empty: 'tiles/empty.png'
}

@define
class Env:
    state: field
    x_size: int
    y_size: int
    direction: Direction
    pos: Tuple
    actions: set = {Direction.left, Direction.right, Direction.up, Direction.down }

    def __str__(self):
        return f"Env(state={self.state}, size={self.x_size}, {self.y_size}, direction={self.direction}, pos={self.pos})"

    def get_possible_actions(self):
        actions = self.actions.copy()
        actions.remove(OPPOSITE_DIRECTION[self.direction])
        possible_actions = []
        for action in actions:
            if self.is_possible_action(action):
                possible_actions.append(action)
        return possible_actions

    def get_field(self,x,y):
        idx = x + self.x_size*y
        return self.state[idx]

    def apply(self, action):
        x,y = self.pos
        state_idx = x + self.x_size*y
        if self.direction == Direction.left:
            if action == Direction.up:
                self.state[state_idx]=Field.left_lower
            elif action == Direction.down:
                self.state[state_idx]=Field.left_upper
            elif action == Direction.left:
                self.state[state_idx]=Field.horizontal
        elif self.direction == Direction.right:
            if action == Direction.up:
                self.state[state_idx]=Field.right_lower
            elif action == Direction.down:
                self.state[state_idx]=Field.right_upper
            elif action == Direction.right:
                self.state[state_idx]=Field.horizontal
        elif self.direction == Direction.up:
            if action == Direction.left:
                self.state[state_idx]=Field.right_upper
            if action == Direction.right:
                self.state[state_idx]=Field.left_upper
            elif action == Direction.up:
                self.state[state_idx]=Field.vertical
        elif self.direction == Direction.down:
            if action == Direction.left:
                self.state[state_idx]=Field.right_lower
            elif action == Direction.right:
                self.state[state_idx]=Field.left_lower
            elif action == Direction.down:
                self.state[state_idx]=Field.vertical
        
        print(f"old direction={self.direction}, action={action}, state_idx={state_idx}, field={self.state[state_idx]}")

        if action == Direction.up:
            y-=1
        elif action == Direction.down:
            y+=1
        elif action == Direction.left:
            x-=1
        elif action == Direction.right:
            x+=1

        # update state
        self.direction = action
        self.pos = (x, y)

    def is_possible_action(self, action):
        x,y = self.pos
        if action == Direction.up:
            if self.direction == Direction.down:
                return False
            y-=1
        elif action == Direction.down:
            if self.direction == Direction.up:
                return False
            y+=1
        elif action == Direction.left:
            if self.direction == Direction.right:
                return False
            x-=1
        elif action == Direction.right:
            if self.direction == Direction.left:
                return False
            x+=1
        
        if x<0 or y<0 or x>=self.x_size or y>=self.y_size:
            return False
        else:
            # the next field to occupy must either be empty or it is the start field, when we are back
            return self.state[x+y*self.x_size]==Field.empty or \
                x==y==0



class Visualize:
    TILE_SIZE_X = 172
    TILE_SIZE_Y = 174
    @staticmethod
    def visualize(env: Env):
        x_size = env.x_size
        y_size = env.y_size
        img = Image.new(mode='RGB', size=(Visualize.TILE_SIZE_X*x_size, Visualize.TILE_SIZE_Y*y_size))
        for y in range(env.y_size):
            pos_y = y * Visualize.TILE_SIZE_Y
            for x in range(env.x_size):
                pos_x = x * Visualize.TILE_SIZE_X
                pos=(pos_x,pos_y)
                field = env.get_field(x,y)
                print(f"visualize {field} at pos {pos}")
                field_img = field_images[field]
                tile = Image.open(field_img)
                img.paste(tile,pos)
        img.save('output/out.png')

class FieldToTensor:
    @staticmethod
    def to_tensor(env: Env, device="cpu"):
        x_size = env.x_size
        y_size = env.y_size
        channels = len(Field.values)
        tensor = torch.ones([x_size,y_size,channels], dtype=torch.float32, device=device)
        for y in range(env.y_size):
            for x in range(env.x_size):
                field = env.get_field(x,y)
                ordinal = Field.ordinal(field)
                print(field, ordinal)
                
class EnvBuilder:
    @staticmethod 
    def build(size_x, size_y):
        state = [Field.empty] * (size_x * size_y)
        return Env(state, size_x, size_y, direction=Direction.left, pos=(0,0))

def rollout(env):
    print(env)
    possible_actions = env.get_possible_actions()
    while len(possible_actions)>0:
        action = np.random.choice(possible_actions,1)[0]
        print(f"action={action}")
        env.apply(action)
        possible_actions = env.get_possible_actions()
    print("done")
    print(env)


env = EnvBuilder.build(5,5)
rollout(env)
Visualize.visualize(env)
#FieldToTensor.to_tensor(env)


