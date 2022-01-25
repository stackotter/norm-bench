#written by boboquack + copilot

#guide to use
#you can use the configurable settings to change the input word list and some miscellaneous variables
#otherwise, you should really only need to call rand_board() (perhaps with some arguments)
#feel free to remove the import of random if you already have that in your namespace

#begin configurable settings

# selectiondistribution is a mysterious variable that controls how long the branches in the crossword are during generation
# generate_example_board is a boolean that controls whether or not an example is to be printed to the console
selectiondistribution=[3,4,4,5]
generate_example_board=False

#derivedwords is a function that returns its input + any words that look "similar". currently there is no actual checking of similarity
def derivedwords(word):
    return {word}

if generate_example_board:
    # minwordlen specifies the minimum length of a word to be considered
    # topwordlen specifies the length of the top word to be used (i.e. the number of letters at the bottom of the screen)
    # boardheight specifies the maximum board height in rows
    # boardwidth specifies the maximum board width in columns
    minwordlen=3
    topwordlen=7
    boardheight=20
    boardwidth=20

#get words from a file - can be changed to any source of words. make sure the words are all lowercase and no punctuation
fin=open("UKACD18plus.txt","r")
allwords=[i for i in fin.read().split('\n') if i==i.lower() and i.isascii() and i.isalpha()]

#end configurable settings

#begin preprocessing

#some preprocessing allowing us to easily test if something is an iterated transdeletion
alphabet='abcdefghijklmnopqrstuvwxyz'
lcounts={}
for i in allwords:
    lcounts[i]={j:0 for j in alphabet}
    for j in i:
        lcounts[i][j]+=1

#some preprocessing allowing us to easily pick a starting word
wbylen={}
for word in allwords:
    if len(word) in wbylen:
        wbylen[len(word)].append(word)
    else:
        wbylen[len(word)]=[word]

import random

#print('Resources loaded!')

#end preprocessing

#the board class. you shouldn't need to create an instance directly, but you'll get board as an output from rand_board. 
# use board.output() to get the positions of words on the board as a list of (x, y, dir, word) tuples
# use repr(board) to get a text representation of the placement of letters on the board
class board:
    def __init__(self,height,width,noextensions=False):
        self.grid=[[' ']*width for i in range(height)]
        self.words=[]
        self.height=height
        self.width=width
        self.tidycount=0
        self.debug=False
        self.noextensions=noextensions

    #translates the board to a list of (x,y,dir,word) tuples
    def output(self):
        out=[]
        lookup={'d':'down','a':'across'}
        for word,r,c,dir in self.words:
            out.append((c,r,lookup[dir],word))
        return out

    #ensures no 2x2 square is completely filled
    def fill22(self):
        for r in range(self.height-1):
            for c in range(self.width-1):
                if self.grid[r][c].isalpha() and self.grid[r][c+1].isalpha() and self.grid[r+1][c].isalpha():
                    self.grid[r+1][c+1]='_'
                if self.grid[r][c].isalpha() and self.grid[r][c+1].isalpha() and self.grid[r+1][c+1].isalpha():
                    self.grid[r+1][c]='_'
                if self.grid[r][c].isalpha() and self.grid[r+1][c].isalpha() and self.grid[r+1][c+1].isalpha():
                    self.grid[r][c+1]='_'
                if self.grid[r+1][c].isalpha() and self.grid[r][c+1].isalpha() and self.grid[r+1][c+1].isalpha():
                    self.grid[r][c]='_'
    
    #adds some extra spaces to ensure no word is completely checked
    def tidy(self):
        self.fill22()
        while self.tidycount<len(self.words):
            word,r,c,dir=self.words[self.tidycount]
            if dir=='a':
                if c>0:
                    self.grid[r][c-1]='_'
                if c+len(word)<self.width:
                    self.grid[r][c+len(word)]='_'
                blankpos=[]
                for i in range(len(word)):
                    if (r==0 or self.grid[r-1][c+i]=='_') and (r==self.height-1 or self.grid[r+1][c+i]=='_'):
                        break
                    if not((r>0 and self.grid[r-1][c+i].isalpha()) or (r<self.height-1 and self.grid[r+1][c+i].isalpha())):
                        blankpos.append(i)
                else:
                    if len(blankpos)==0:
                        self.setdebug()
                        raise ValueError(f"{word} at {r},{c},{dir} is not tidyable\n{self}\n{self.words}")
                    else:
                        i=random.choice(blankpos)
                        if r>0:
                            self.grid[r-1][c+i]='_'
                        if r<self.height-1:
                            self.grid[r+1][c+i]='_'
            if dir=='d':
                if r>0:
                    self.grid[r-1][c]='_'
                if r+len(word)<self.height:
                    self.grid[r+len(word)][c]='_'
                blankpos=[]
                for i in range(len(word)):
                    if (c==0 or self.grid[r+i][c-1]=='_') and (c==self.width-1 or self.grid[r+i][c+1]=='_'):
                        break
                    if not((c>0 and self.grid[r+i][c-1].isalpha()) or (c<self.width-1 and self.grid[r+i][c+1].isalpha())):
                        blankpos.append(i)
                else:
                    if len(blankpos)==0:
                        self.set_debug()
                        raise ValueError(f"{word} at {r},{c},{dir} is not tidyable\n{self}\n{self.words}")
                    else:
                        i=random.choice(blankpos)
                        if c>0:
                            self.grid[r+i][c-1]='_'
                        if c<self.width-1:
                            self.grid[r+i][c+1]='_'
            self.tidycount+=1

    #adds a word to the board and checks no derived word is already on there and there are no conflicts
    def add_word(self,word,r,c,dir):
        dwords=derivedwords(word)
        assert not any(i in dwords for i in self.words)
        self.words.append((word,r,c,dir))
        if dir=='a':
            assert len(word)+c<=self.width
            for i in range(len(word)):
                if (self.grid[r][c+i].isalpha() and self.grid[r][c+i]!=word[i]) or self.grid[r][c+i]=='_':
                    self.set_debug()
                    raise ValueError(f"{word} placed at {r},{c},{dir} conflicts with {self.grid[r][c+i]} at {r},{c+i}\n{self}\n{self.words}")
                self.grid[r][c+i]=word[i]
        elif dir=='d':
            assert len(word)+r<=self.height
            for i in range(len(word)):
                if (self.grid[r+i][c].isalpha() and self.grid[r+i][c]!=word[i]) or self.grid[r+i][c]=='_':
                    self.set_debug()
                    raise ValueError(f"{word} placed at {r},{c},{dir} conflicts with {self.grid[r+i][c]} at {r+i},{c}\n{self}\n{self.words}")
                self.grid[r+i][c]=word[i]
        else:
            raise ValueError(f"Invalid direction: {dir}")
    
    #counts the number of words on the board
    def num_words(self):
        return len(self.words)

    #sets the debug flag for output
    def set_debug(self):
        self.debug=True

    #removes the debug flag for output
    def remove_debug(self):
        self.debug=False

    #outputs a spatial representation of letter positioning
    def __repr__(self):
        if self.debug:
            s=[''.join(row) for row in self.grid]
            v=0
            while all(i==' ' for i in s[0]):
                s=s[1:]
                v+=1
            w=0
            while all(i==' ' for i in s[-1]):
                s=s[:-1]
                w+=1
            return '. '+str(v)+'\n'+'\n'.join(s)+'\n. '+str(w)
        s=[''.join(row).replace('_',' ') for row in self.grid]
        while all(i==' ' for i in s[0]):
            s=s[1:]
        while all(i==' ' for i in s[-1]):
            s=s[:-1]
        while all(i[0]==' ' for i in s):
            s=[i[1:] for i in s]
        while all(i[-1]==' ' for i in s):
            s=[i[:-1] for i in s]
        return '\n'.join(s).upper()
        

    #tries to return a scaffold for potential new word placements in the form 
    # a) locs as (r;c;dir) 
    # b) words as ('.'s for blanks, '2' to connect right, '1' to connect left, letter to connect;free on the left;free on the right)
    def get_scaffold(self,self_loop=True):
        dirs={'u':(-1,0),'d':(1,0),'l':(0,-1),'r':(0,1)}
        sidea={'u':(0,1),'d':(0,-1),'l':(1,0),'r':(-1,0)}
        sideb={'u':(0,-1),'d':(0,1),'l':(-1,0),'r':(1,0)}
        trans={'u':['l','r'],'d':['l','r'],'l':['u','d'],'r':['u','d']}

        ranger=list(range(self.height))
        random.shuffle(ranger)
        rangec=list(range(self.width))
        random.shuffle(rangec)
        for r in ranger:
            for c in rangec:
                if self.grid[r][c].isalpha():
                    for dir in dirs:
                        dr,dc=dirs[dir]
                        if 0<=r+dr<self.height and 0<=c+dc<self.width:
                            if self.grid[r+dr][c+dc]==' ':
                                try:
                                    try:
                                        nr=r
                                        nc=c
                                        store=[]
                                        newgrid=[i[:] for i in self.grid]
                                        while True:
                                            dr,dc=dirs[dir]
                                            ar,ac=sidea[dir]
                                            br,bc=sideb[dir]
                                            dist=random.choice(selectiondistribution)
                                            for i in range(dist-1):
                                                nr+=dr
                                                nc+=dc
                                                if not(0<=nr<self.height and 0<=nc<self.width):
                                                    raise ZeroDivisionError
                                                store.append((nr,nc,dir))
                                                if newgrid[nr][nc]=='_':
                                                    raise ZeroDivisionError
                                                if newgrid[nr][nc].isalpha() or newgrid[nr][nc]=='$':
                                                    if newgrid[nr][nc]=='$' and not self_loop:
                                                        raise ZeroDivisionError
                                                    xr=nr+dr
                                                    xc=nc+dc
                                                    if 0<=xr<self.height and 0<=xc<self.width and \
                                                        (newgrid[xr][xc].isalpha() or newgrid[xr][xc]=='$'):
                                                        raise ZeroDivisionError
                                                    raise BufferError
                                                if 0<=nr+ar<self.height and 0<=nc+ac<self.width and \
                                                (newgrid[nr+ar][nc+ac].isalpha() or newgrid[nr+ar][nc+ac]=='$'):
                                                    raise ZeroDivisionError
                                                if 0<=nr+br<self.height and 0<=nc+bc<self.width and \
                                                (newgrid[nr+br][nc+bc].isalpha() or newgrid[nr+br][nc+bc]=='$'):
                                                    raise ZeroDivisionError
                                                newgrid[nr][nc]='$'
                                            dir=random.choice(trans[dir])
                                    except BufferError:
                                        #self.set_debug()
                                        #print(self.words)
                                        #print(self)
                                        #print(store)
                                        split=[[store[0]]]
                                        for i in store[1:]:
                                            if i[2]==split[-1][-1][2]:
                                                split[-1].append(i)
                                            else:
                                                split.append([i])
                                        #print(split)
                                        newsplit=[[(i[0][0]*2-i[1][0],i[0][1]*2-i[1][1]),(i[-1][0],i[-1][1])] for i in split]
                                        newersplit=[i[:] for i in newsplit]
                                        for i in newersplit:i.sort()
                                        locs=[]
                                        for i in newersplit:
                                            if i[0][0]==i[1][0]:
                                                locs.append((i[0][0],i[0][1],'a'))
                                            else:
                                                locs.append((i[0][0],i[0][1],'d'))
                                        #print(newsplit)
                                        #print(newersplit)
                                        #print(loc)
                                        patterns=[['.'*(abs(x[0]+x[1]-y[0]-y[1])-1),None,None] for x,y in newsplit]
                                        if len(patterns)==1:
                                            if newsplit[0][0]==newersplit[0][0]:
                                                patterns[0][0]=newgrid[newsplit[0][0][0]][newsplit[0][0][1]]+patterns[0][0]+newgrid[newsplit[0][1][0]][newsplit[0][1][1]]
                                            else:
                                                patterns[0][0]=newgrid[newsplit[0][1][0]][newsplit[0][1][1]]+patterns[0][0]+newgrid[newsplit[0][0][0]][newsplit[0][0][1]]
                                        if len(patterns)>1:
                                            if newsplit[0][0]==newersplit[0][0]:
                                                patterns[0][0]=newgrid[newsplit[0][0][0]][newsplit[0][0][1]]+patterns[0][0]+'2'
                                            else:
                                                patterns[0][0]='2'+patterns[0][0]+newgrid[newsplit[0][0][0]][newsplit[0][0][1]]
                                            if newsplit[-1][0]==newersplit[-1][0]:
                                                patterns[-1][0]='1'+patterns[-1][0]+newgrid[newsplit[-1][1][0]][newsplit[-1][1][1]]
                                            else:
                                                patterns[-1][0]=newgrid[newsplit[-1][1][0]][newsplit[-1][1][1]]+patterns[-1][0]+'1'
                                        for i in range(1,len(patterns)-1):
                                            if newsplit[i][0]==newersplit[i][0]:
                                                patterns[i][0]='1'+patterns[i][0]+'2'
                                            else:
                                                patterns[i][0]='2'+patterns[i][0]+'1'
                                        if '$' in patterns[-1][0]:
                                            zr,zc=newsplit[-1][1][0],newsplit[-1][1][1]
                                            for i in range(len(patterns)):
                                                if (zr,zc)==newersplit[i][0] or (zr,zc)==newersplit[i][1]:
                                                    raise ZeroDivisionError
                                                if newersplit[i][0][0]<=zr<=newersplit[i][1][0] and \
                                                newersplit[i][0][1]<=zc<=newersplit[i][1][1]:
                                                    if len(patterns[i])==3:
                                                        raise ZeroDivisionError
                                                    val=abs(zr+zc-newersplit[i][0][0]-newersplit[i][0][1])
                                                    patterns[i][0]=patterns[i][0][:val]+'$'+patterns[i][0][val+1:]
                                                    break
                                            else:
                                                raise ValueError("Unexpected behaviour with $ finding")
                                        #print(patterns)
                                        if self.noextensions:
                                            patterns=[(i,0,0) for i,j,k in patterns]
                                            return locs,patterns
                                        
                                        for i in patterns:
                                            i[1]=0
                                            i[2]=0

                                        pattlook={'u':1,'d':2,'l':1,'r':2}
                                        dirfind={'a':['l','r'],'d':['u','d']}
                                        worddirs=[(i,dirfind[locs[i][2]][0]) for i in range(len(locs))] + \
                                                    [(i,dirfind[locs[i][2]][1]) for i in range(len(locs))]
                                        
                                        while len(worddirs)>0:
                                            i,dir=random.choice(worddirs)
                                            er,ec=dirs[dir]
                                            qr,qc=newersplit[i][pattlook[dir]-1]
                                            edist=patterns[i][pattlook[dir]]+1
                                            qr,qc=qr+er*edist,qc+ec*edist
                                            aar,aac=sidea[dir]
                                            bbr,bbc=sideb[dir]
                                            if 0<=qr<self.height and 0<=qc<self.width and \
                                                newgrid[qr][qc]==' ' and \
                                                not(0<=qr+aar<self.height and 0<=qc+aac<self.width and \
                                                    (newgrid[qr+aar][qc+aac].isalpha() or newgrid[qr+aar][qc+aac]=='$')) and \
                                                not(0<=qr+bbr<self.height and 0<=qc+bbc<self.width and \
                                                    (newgrid[qr+bbr][qc+bbc].isalpha() or newgrid[qr+bbr][qc+bbc]=='$')) and \
                                                not(0<=qr+er<self.height and 0<=qc+ec<self.width and \
                                                    (newgrid[qr+er][qc+ec].isalpha() or newgrid[qr+er][qc+ec]=='$')):
                                                patterns[i][pattlook[dir]]+=1
                                                newgrid[qr][qc]='$'
                                            else:
                                                worddirs.remove((i,dir))

                                        patterns=[(i,j,k) for i,j,k in patterns]
                                        #self.set_debug()
                                        #print(self.words)
                                        #print(self)
                                        #print(locs)
                                        #print(patterns)
                                        return locs,patterns
                                except ZeroDivisionError:
                                    continue
        return None,None

#helper function that checks if a word matches the pattern given by the scaffold
#you shouldn't call this directly
def match(word,thispatt,left,right,possibilities):
    if len(word)<len(thispatt) or len(word)>left+right+len(thispatt):
        return None
    valid=[]
    for prefix in range(max(0,len(word)-len(thispatt)-right),1+min(left,len(word)-len(thispatt))):
        link='1'
        for j in range(len(thispatt)):
            if thispatt[j].isalpha() and word[prefix+j]!=thispatt[j]:
                break
            if thispatt[j]=='1':
                if word[prefix+j] not in possibilities or word in possibilities[word[prefix+j]]['bad']:
                    break
                else:
                    link=word[prefix+j]
        else:
            valid.append({'letter':link,'displacement':prefix})
    if valid:
        return random.choice(valid)
    return None

#tries to fill a scaffold with words from the list of words
#you shouldn't call this directly
def get_fill(letters,words,scaffoldx):
    if any('$' in i for i,l,r in scaffoldx):
        val=letters[:]
        random.shuffle(val)
    else:val=['$']
    for newval in val:
        scaffold=[(i.replace('$',newval),l,r) for i,l,r in scaffoldx]
        #print(scaffold)
        possibilities={'1':{'bad':set(),'fill':[]}}
        for patt,left,right in scaffold:
            newpossibilities={}
            random.shuffle(letters)
            for letter in letters:
                thispatt=patt.replace('2',letter)
                valid=[]
                for word in words:
                    if link:=match(word,thispatt,left,right,possibilities):
                        valid.append((word,link))
                if valid:
                    word,link=random.choice(valid)
                    newpossibilities[letter]={'bad':possibilities[link['letter']]['bad']|derivedwords(word),
                                            'fill':possibilities[link['letter']]['fill']+[(word,link['displacement'])]}
            possibilities=newpossibilities
            if not possibilities:return None
        return possibilities[letters[0]]['fill']

#creates a board given the main word and a list of words that can be made from the letters of mainword (plus dimensions and retries)
#you can call this directly if you want but you shouldn't need to
def create_board(mainword,words,maxheight=20,maxwidth=20,maxretries=1000):
    letters=list(set(mainword))
    assert all(all(i in letters for i in j) for j in words)

    grid=board(maxheight,maxwidth)
    #grid.set_debug()
    firstdir=random.choice(['a','d'])
    if firstdir=='a':
        if len(mainword)>maxwidth:return None
        r=random.randint(0,maxheight-1)
        c=random.randint(0,maxwidth-len(mainword))
        grid.add_word(mainword,r,c,'a')
    else:
        if len(mainword)>maxheight:return None
        r=random.randint(0,maxheight-len(mainword))
        c=random.randint(0,maxwidth-1)
        grid.add_word(mainword,r,c,'d')
    words-=derivedwords(mainword)
    grid.tidy()
    
    #next we need to generate the first loop off the main word

    retries=maxretries
    while grid.num_words()==1 and retries>0:
        retries-=1
        locs,scaffold=grid.get_scaffold(False)
        if not locs:continue
        
        fill=get_fill(letters,words,scaffold)
        if not fill:continue

        for loc,data in zip(locs,fill):
            word,displacement=data
            words-=derivedwords(word)
            r,c,dir=loc
            if dir=='a':
                grid.add_word(word,r,c-displacement,dir)
            else:
                grid.add_word(word,r-displacement,c,dir)
        grid.tidy()
        #print(grid)

    if grid.num_words()==1:
        return None

    #now we should try to keep generating loops

    num_words=grid.num_words()
    retries=maxretries
    while grid.num_words()!=num_words or retries>0:
        if grid.num_words()!=num_words:
            num_words=grid.num_words()
            retries=maxretries
        
        retries-=1
        locs,scaffold=grid.get_scaffold()
        if not locs:continue

        fill=get_fill(letters,words,scaffold)
        if not fill:continue

        for loc,data in zip(locs,fill):
            word,displacement=data
            for i in derivedwords(word):
                words.remove(i)
            r,c,dir=loc
            if dir=='a':
                grid.add_word(word,r,c-displacement,dir)
            else:
                grid.add_word(word,r-displacement,c,dir)
        grid.tidy()
        #print(grid)

    return grid

#returns all words that can be made from the letters of the main word
#you can call this directly if you want but you shouldn't need to
def subs(mainword,minlen):
    resp=set()
    for word in allwords:
        if len(word)>=minlen and all(lcounts[word][i]<=lcounts[mainword][i] for i in alphabet):
            resp.add(word)
    return resp

#selects a random main word and tries to create a board with it, trying maxretries times
#you can call this directly
def rand_board(minlen=3,toplen=7,height=20,width=20,maxretries=10):
    if minlen>toplen or toplen not in wbylen:
        return None
    resp=None
    retries=maxretries
    while not resp and retries>0:
        retries-=1
        mainword=random.choice(wbylen[toplen])
        resp=create_board(mainword,subs(mainword,minlen),height,width)
    if resp:
        return resp
    return None

# some code to generate an example board
if generate_example_board:
    the_board=rand_board(minwordlen,topwordlen,boardheight,boardwidth)
    if the_board:
        #the_board.set_debug()
        print(the_board)
    else:
        print("No board found")

