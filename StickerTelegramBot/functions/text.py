from loader import dp, bot
from data.sqlite import *
import aiohttp

from json import loads
from json.decoder import JSONDecodeError

from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

# -*- coding: utf-8 -*-
import textwrap
from io import BytesIO
from typing import List, Dict, Optional

from PIL import Image, ImageDraw, ImageFilter, ImageOps
from PIL import ImageFont
from aiogram.types import Message

async def get_fontsize(image, text):
	fontsize = 1  
	img_fraction = 0.9

	font = ImageFont.truetype("functions/arial.ttf", fontsize)
	while font.getbbox(text)[2]-font.getbbox(text)[0] < img_fraction*image.size[0]:
		fontsize += 1
		font = ImageFont.truetype("functions/arial.ttf", fontsize)

	fontsize -= 1
	font = ImageFont.truetype("functions/arial.ttf", fontsize)
	return font

async def draw_multiple_line_text(image, text, text_color, shadow_color):
	draw = ImageDraw.Draw(image)
	image_width, image_height = image.size
	y_text = image_height//2
	lines = textwrap.wrap(text, width=40)
	font = await get_fontsize(image, lines[0])
	for line in lines:
		l, t, r, b = font.getbbox(line)
		line_width, line_height = r-l, b-t
		draw.text(((image_width - line_width) / 2, y_text-line_height), 
				  line, font=font, fill=text_color)
		draw.text((((image_width - line_width) / 2)-2, (y_text-line_height)-2), 
				  line, font=font, fill=shadow_color)
		y_text += line_height

async def get_image_text(output, color, text):
	image = Image.open('functions/_photo_.png')
	await draw_multiple_line_text(image, text, color[1], color[0])

	image.thumbnail(size=(512, 512))
	image.save(output, 'PNG')
	image.close()
	return output



OPEN_SANS = ImageFont.truetype('functions/arial.ttf', 26)

FONT_SIZE=24

AVATAR_SIZE=50

AVATAR_MARGIN=5

BUBBLE_X_START= AVATAR_SIZE + AVATAR_MARGIN
BUBBLE_RADIUS=20
BUBBLE_PADDING=BUBBLE_RADIUS

TEXT_X_START= BUBBLE_X_START + BUBBLE_PADDING

class BubbleDrawer:
	img: Image.Image
	avatar: Optional[Image.Image]
	message: Message

	def __init__(self, msg):
		self.message = msg
		self.avatar = None

	@property
	def _name(self) -> str:
		try:
			result = self.message.from_user.first_name
			if self.message.from_user.last_name:
				result += " " + self.message.from_user.last_name
			return result
		except (KeyError, TypeError):
			return self.message.from_user.first_name

	@property
	def _shortname(self) -> str:
		return self._name[0].upper()

	@property
	def _text(self) -> List[str]:
		return textwrap.wrap(self.message["text"], width=30)

	def set_avatar(self, data) -> None:
		# Open original image
		avatar = Image.open(data)  # type: Image.Image

		# Resize it to avatar size, assuming it's already square
		size = (AVATAR_SIZE, AVATAR_SIZE)
		avatar = avatar.resize(size, Image.LANCZOS)

		# Make circle with mask
		mask = Image.new('L', size, 0)
		draw = ImageDraw.Draw(mask)
		draw.ellipse((0, 0) + size, fill=255)

		self.avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
		self.avatar.putalpha(mask)

	def draw(self) -> None:
		# Calculate size of sticker
		# width is constant and fixed to 512

		res = OPEN_SANS.getbbox(self._text[0])[3] - OPEN_SANS.getbbox(self._text[0])[1]
		font_height = res
		width = 512
		height = font_height * (len(self._text) + 1) + 2*BUBBLE_PADDING

		if height > 512:
			raise OverflowError("Image too big")

		self.img = Image.new('RGBA', (width, height), color=(255, 255, 255, 0))

		d = ImageDraw.Draw(self.img)

		# Draw avatar circle
		if self.avatar:
			# Image present, just insert it
			self.img.paste(self.avatar, (0, 0))
		else:
			# Draw circle
			d.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=(64, 167, 227, 255))
			shir = OPEN_SANS.getbbox(self._shortname)[2] - OPEN_SANS.getbbox(self._shortname)[0]
			vis = OPEN_SANS.getbbox(self._shortname)[3] - OPEN_SANS.getbbox(self._shortname)[1]
			position = (
				(AVATAR_SIZE / 2) - (shir / 2),
				(AVATAR_SIZE / 2) - (vis / 2) - 4,
			)
			d.text(
				position,
				self._shortname,
				fill="white",
				font=OPEN_SANS
			)

		# Draw message bubble
		d.rounded_rectangle((BUBBLE_X_START, 0, width, height), fill="black", radius=BUBBLE_RADIUS)

		# Draw title, a.k.a. name of sender
		d.text((TEXT_X_START, BUBBLE_PADDING), self._name, fill="pink", font=OPEN_SANS)

		# Draw message body
		offset = BUBBLE_PADDING + font_height
		for line in self._text:
			d.text((TEXT_X_START, offset), line, fill="white", font=OPEN_SANS)
			offset += font_height

	def show(self) -> None:
		if self.img is None:
			return

		self.img.show()

	def save(self, filename) -> None:
		if self.img is None:
			return

		self.img.thumbnail(size=(512,512))
		self.img.save(filename, 'PNG')