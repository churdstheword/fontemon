#! /bin/python3

# Lets solve the fontemon game!
# https://www.coderelay.io/fontemon.html#player

import numpy as np
import io
import cv2
from PIL import ImageFont, ImageDraw, Image


def drawFrameToFile(frame, filename='./images/output.png'):
    width, height = (250, 250)
    image = Image.new(mode="L", size=(width - 1, height - 1), color=(255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("./fonts/fontemon_small.otf", 100)
    draw.text(xy=(0, 100), text=frame, color=(255), font=font)
    image.save(filename)
    return image


def drawFrameToBuffer(frame):
    width, height = (250, 250)
    image = Image.new(mode="L", size=(width - 1, height - 1), color=(255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("./fonts/fontemon_small.otf", 100)
    draw.text(xy=(0, 100), text=frame, color=(0), font=font)
    buffer = io.BytesIO()
    image.save(buffer, format='png')
    buffer.seek(0)
    return buffer


def imageFileContainsFile(file1, file2):
    return (
        cv2.matchTemplate(
            cv2.imread(file1, cv2.IMREAD_GRAYSCALE),
            cv2.imread(file2, cv2.IMREAD_GRAYSCALE),
            cv2.TM_CCOEFF_NORMED
        ) > 0.95
    )


def imageBufferContainsBuffer(file1, file2):
    return (
        cv2.matchTemplate(
            cv2.imdecode(np.frombuffer(file1.getbuffer(), dtype=np.uint8), cv2.IMREAD_GRAYSCALE), 
            cv2.imdecode(np.frombuffer(file2.getbuffer(), dtype=np.uint8), cv2.IMREAD_GRAYSCALE),
            cv2.TM_CCOEFF_NORMED
        ) > 0.95
    )


def serializeFrame(frame):
    shorthand = []
    length = len(frame)
    left = -1
    for right in range(0, length):
        if right == (length - 1) or frame[right] != frame[right + 1]:
            shorthand.append([frame[right], right - left])
            left = right
    return shorthand


def unserializeFrame(shorthand):
    frame = ''
    for i in range(0, len(shorthand)):
        frame = frame + (shorthand[i][0] * shorthand[i][1])
    return frame


def solve(startFrame=''):
    frame = startFrame
    frameIndex = len(startFrame)
    done = False
    frameCheckValue = 150

    while (not done) and (frameIndex < 5000):

        images = {}
        for nextFrame in ['a', 'b', 'c', 'd']:
            images[nextFrame] = drawFrameToBuffer(
                frame + nextFrame + 'x' * (frameCheckValue))

        result1 = imageBufferContainsBuffer(images['a'], images['b'])
        result2 = imageBufferContainsBuffer(images['a'], images['c'])
        result3 = imageBufferContainsBuffer(images['a'], images['d'])

        images = None

        if(not result1 or not result2 or not result3):
            newFrame = frame[len(startFrame)::]
            with open('logs.txt', 'a') as file:
                file.write('FORK: ' + str(serializeFrame(frame)) + "\n")
            for nextFrame in ['a', 'b', 'c', 'd']:
                solve(startFrame + 'x' * len(newFrame) + nextFrame)
            done = True
            break

        # Advance to the next frame
        frame = frame + 'x'
        frameIndex += 1

        # Draw the frame
        drawFrameToFile(frame)

        # Check for certain game states
        if(imageFileContainsFile('./images/output.png', './images/lost.png')):
            with open('logs.txt', 'a') as file:
                file.write('GAMEOVER: ' + str(serializeFrame(frame)) + "\n")
            done = True
            break

        if(imageFileContainsFile('./images/output.png', './images/fin.png')):
            with open('logs.txt', 'a') as file:
                file.write('FIN: ' + str(serializeFrame(frame)) + "\n")
            done = True
            break


def main():
    # frameInit = unserializeFrame([['x', 173], ['b', 1], ['x', 157], ['a', 1], ['x', 26], ['a', 1], ['x', 94], ['a', 1]])
    frameInit = unserializeFrame([['x', 160]])
    solve(frameInit)


if __name__ == '__main__':
    main()
