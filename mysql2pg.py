import re
'''
   SQL语句转换，支持MySQL到PostgreSQL的转换
'''
class MySQL2PG(object):
	def __init__(self):
		self.scripts = ''
		self.openParen = 0
		self.closeParen = 0
		self.table = ''
		self.tabComments = ''
		self.indexes = ''
		self.colComments = ''
		self.mapType = {
		    'decimal': 'numeric'
		}
	
	def run(self, file):
		commandType = ''
		with open(file, 'r', encoding='utf8') as f:
			for line in f.readlines():
				if commandType == 'create':
					self.processCreate(line)
					
				if self.scripts.rstrip('\n').rstrip(' ').endswith(';') \
				   and commandType != '':
					commandType = ''
					continue
					
					
				if commandType == '':
					if line.lstrip(' ').startswith('CREATE TABLE'):
						commandType = 'create'
						self.table = re.split(r'[ ]+', line)[2]
						self.processCreate(line)
					elif line.lstrip(' ').startswith('INSERT INTO'):
						commandType = ''
						self.scripts += line
					else:
						commandType = ''
						self.scripts += line
	
	def processCreate(self, line):
		if line.find('(') >= 0:
			self.openParen += 1
		if line.find(')') >= 0:
			self.closeParen += 1
		line = line.strip(' ')
	
		if self.openParen > self.closeParen:
			ignoreType = False
			# 列注释
			if line.lower().find('comment') > 0:
				column = re.split(r'[ ]', line)[0].strip('(')
				desc =  re.split(r'COMMENT', line)[1].strip(' ').strip(')').rstrip(',\n')				
				self.colComments += 'COMMENT ON COLUMN ' + self.table + '.' + column + ' IS ' + desc + ';\n'
				line = ' ' * 4 + line.split('COMMENT')[0].strip(' ').strip('\t') + ',' + '\n'
	
			# 索引
			if line.lower().startswith('key'):
				p, index, column = re.split(r'[ ]+', line)
				column = re.split(r'[ ]+', line)[2].rstrip(',\n')
				self.indexes += 'CREATE INDEX ' + index + ' on ' + self.table + ' ' + column + ';\n'
				line = ''
				ignoreType = True
				
			# 主外键
			if line.lower().startswith('primary key'):
				line = line
				ignoreType = True
	
			# 字段类型
			if not ignoreType and len(line) > 0:
				lineList = line.strip(' ').split(' ')
				if line.strip(' ').startswith('sort decimal'):
					print(line)
					print(lineList)
					
				lineList[1] = lineList[1].replace('decimal', 'numeric')
				line = ' '.join(lineList)

			self.scripts += ' ' * 4 + line.strip(' ').strip('\t') if self.openParen > 1 else line
				
	
		elif self.closeParen == self.openParen:
			# 表级属性
			if line.find('ENGINE') >= 0:
				lineList = re.split(r'[ ]', line)
				tmpList = []
				for i in lineList:
					if i.split('=')[0] in ('COMMENT'):
						self.tabComments = 'COMMENT ON TABLE ' + self.table + ' IS ' + i.split('=')[1].strip(';\n') + ';\n'
	
	
	
			# 重构建表语句
			# 如果是to GPDB 需要在这里添加分布键
			self.scripts = self.scripts.rstrip( ).strip(',\n') + '\n);\n'
			self.scripts += self.indexes
			self.scripts += self.tabComments
			self.scripts += self.colComments
	
			self.indexes  = self.tabComments = self.colComments = ''
			self.closeParen = self.openParen = 0
			
		
	def out(self):
		with open('d:\\abc.sql', 'w', encoding='utf8') as f:
			f.write(self.scripts)		


if __name__ == '__main__':
	mp = MySQL2PG()
	mp.run('c:\\abc.sql')
	mp.out()








