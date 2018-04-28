# -*- coding:utf-8 -*-
'''
批量转换脚本中的关键字为大写
'''
import sys, re

# 所有关键字
Keywords = [
    'select', 'update', 'delete', 'insert' ,'from','set' ,'into' ,'values'
    'distinct', 'count', 'sum', 'avg', 'max', 'min', 'round',
    'over', 'with', 'partition', 'by', 'as', 'date', 'interval', 
    'where', 'using', 'left', 'inner', 'right', 'full', 'on', 'between', 'and', 
    'group', 'having', 'rollup', 'cube', 'grouping', 
    'order', 'desc', 'asc', 'date', 'timestamp', 'varchar', 'text', 
    'smallint','int4', 'bigint','numeric', 'float','time', 'zone', 'null', 'not', 
    'create', 'temp', 'table', 'distributed', 'randomly',
    'primary', 'key', 'foreign', 'references','seria', 'drop', 'alter', 'add'
]

# 需要回车的关键字
NeedEnter = [
    'from','where','and','group','having','order'
]

# 前后需要空格的符号
NeedSpace = [
    '>=', '<=', '+', '-', '>', '<', '=', ','
]

# 用于识别符号前后是为关键字
Symbol = [
    '(', ')', ':', ';'
] + NeedSpace



class FormatSQL(object):
	def __init__(self, filePath=None):
		self.word = ''
		self.notSpace = '@'
		self.scriptContent = []
		self.filePath = filePath if filePath else sys.argv[1]
		if not self.filePath.endswith('.sql'):
			raise Exception("这文件不是SQL文件，请谨慎!!")

	def run(self):		
		with open(self.filePath, 'r', encoding='utf-8') as f:
			# 引号和空格(或回车)标记符
			qmarks = []
			for line in f.readlines():
				if line.strip(' ').startswith('--'):
					self.word = line
					self.flushWord()
					continue
				for i in line:
					# 处理引号：引号内文本不作处理
					if i in ("'", '"'):
						if len(qmarks) > 0 and qmarks[-1] == i:
							qmarks.pop()
							if not qmarks:
								self.word += i	
								self.flushWord()
								continue
						else:
							qmarks.append(i)

					if qmarks:
						self.word += i	
						continue

					# 处理空格：以空格和回车作为单词结束符，并且单词与单词之间只能有一个空格					
					if i in (' ', '\n'):
						if len(self.word) == 0:
							continue
						if i == '\n':
							self.word += i
						self.flushWord()
					# 分割符号与单词
					elif i in Symbol:
						self.flushWord()
						self.word = self.notSpace + i + self.notSpace
						self.flushWord()
					else:
						self.word += i

		self.flushWord()
		#print(self.scriptContent)
		print(self.outContent())


	def flushWord(self):
		if len(self.word) == 0:
			return
		if self.word.endswith(';' + self.notSpace):
			self.word += '\n\n'
		if self.word in Keywords:
			# 部分关键字前需要换行，如果前一个也是关键字就不用换行，比如DELETE FROM、CREATE TEMP TABLE这类语句。
			if self.word in NeedEnter \
			   and self.scriptContent[-1].lower() not in Keywords\
			   and self.scriptContent[-1][-1] != '\n':
				self.word = '\n' + self.word
			self.scriptContent.append(self.word.upper())			
		else:
			self.scriptContent.append(self.word)
		self.word = ''

	def outContent(self):
		flagLen = len(self.notSpace)
		content = ''
		for ind, i in enumerate(self.scriptContent):
			# 前面是换行符直的接拼接
			if (len(content) > 0 and content[-1] == '\n'):
				content += i
			# 如果前一个元素也是NeedSpace元素，而且当前i也是NeedSpace元素，
			# 就需要考虑在这两个元素组合前后留空，而且只能留一个空
			elif self.scriptContent[ind-1].strip(self.notSpace) in NeedSpace \
			     and i.strip(self.notSpace) in NeedSpace:
				content = content.rstrip(' ') + i + ' '
			# 如果前一个不在NeedSpace中而当前i在NeedSpace中就需要在元素前后留空
			elif i.strip(self.notSpace) in NeedSpace:
				content += i + ' ' if i.strip(self.notSpace) == ',' else ' ' + i + ' '
			# 前面是非空占位符拼接
			elif (len(content) > flagLen and content[-flagLen:] == self.notSpace):
				content += i
			# 后面是非空占位符直接拼接
			elif i[:flagLen] == self.notSpace:
				content += i
			else:				
				content += i if content.endswith(' ') else (' ' + i)

		content = content.replace(self.notSpace, '').strip()

		return content


if __name__ == '__main__':
	f = FormatSQL()
	f.run()