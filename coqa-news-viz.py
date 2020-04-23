# Author: Sal Barbosa
# User interface to display linguistic information and scoring of a preprocessed json file containing CNN news stories from the CoQA dataset
# Requires 2 input files:
# 1) coqa-news-preprocessed-final.json - Preprocessed file with tags, parses, corefs from Stanford CoreNLP
# 2) sentence-scores.txt (externally generated): by sentence score (higher is better) for each question against each sentence of the passage
#    the file has 2 columns: col1:passage#.question#.sentence#    col2: the score for that p#.q#.s#
#
import json
from tkinter import *
from PIL import Image, ImageTk
import random

# indices to the token tuples sored in the preprocess file:
TOK = 0              # Token
P_TAG = 1            # Part-of-speech tag
L_TAG = 2            # Lemma tag
N_TAG = 3            # Named-entity tag
M_TAG = 4            # Mapping tag (string index to token index)

# images and widgets dictionary (required by tkinter for permanence)
images = {}
images['rationale'] = []

# Constants for outputting passages/stories
# Consolas 8 font is 6 pixels wide by 8 pixels high
W_GAP = 2       # gap between words
V_GAP = 30      # vertical gap between lines
FONT_W = 6      # font's width
FONT_H = 8      # font's height
X_MIN = 20      # minimum x coordinate of text
X_MAX = 1480    # maximum x coordinate of text
Y_MIN = 40      # minimum y coordinate of text (1st line)

# Constants for outputting questions and answers
Q_X_MAX = 980   # maximum x coordinate for question
Q_Y_MIN = 26    # minimum y coordinate for question
A_Y_MIN = 125   # minimum y coordinate for answer

# POS tag colors
nncolr = '#00FF7F'
vbcolr = '#AB82FF'
jjcolr = '#63B8FF'
rbcolr = '#A2CD5A'
prpcolr = '#FF6A6A'
intocolr = '#FFD700'

# NE tag colors
perscolr = '#B9D3EE'
orgcolr = '#C67171'
loccolr = '#8E8E38'
titlcolr = '#EED5B7'
timecolr = '#B4EEB4'
amtcolr = '#7171C6'

coref_colors = ['#8B475D','#CD6600','#551A8B','#0000CD','#006400','#8B814C','#8B5A00'] # different colors improve coreference viewing

tag_colors = {
'NN*' : {'ttype': 'POS', 'sel' : False, 'color' : '#00FF7F', 'mbrs' : ['NN', 'NNP', 'NNPS', 'NNS']},
'VB*' : {'ttype': 'POS', 'sel' : False, 'color' : '#AB82FF', 'mbrs' : ['MD', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']},
'JJ*' : {'ttype': 'POS', 'sel' : False, 'color' : '#63B8FF', 'mbrs' : ['JJ', 'JJR', 'JJS']},
'PRP*' : {'ttype': 'POS', 'sel' : False, 'color' : '#FF6A6A', 'mbrs' : ['PRP', 'PRP$']},
'RB*' : {'ttype': 'POS', 'sel' : False, 'color' : '#A2CD5A', 'mbrs' : ['RB', 'RBR', 'RBS']},
'IN' : {'ttype': 'POS', 'sel' : False, 'color' : '#FFD700', 'mbrs' : ['IN', 'TO']},

'PER' : {'ttype': 'NE', 'sel' : False, 'color' : '#B9D3EE', 'mbrs' : ['PERSON']},
'ORG' : {'ttype': 'NE', 'sel' : False, 'color' : '#C67171', 'mbrs' : ['ORGANIZATION']},
'LOC' : {'ttype': 'NE', 'sel' : False, 'color' : '#B1B16B', 'mbrs' : ['CITY', 'COUNTRY', 'STATE_OR_PROVINCE', 'LOCATION']},
'TME' : {'ttype': 'NE', 'sel' : False, 'color' : '#B4EEB4', 'mbrs' : ['DATE', 'DURATION', 'TIME']},
'QTY' : {'ttype': 'NE', 'sel' : False, 'color' : '#CDA0ED', 'mbrs' : ['MONEY', 'NUMBER', 'ORDINAL', 'PERCENT']},
'ATR' : {'ttype': 'NE', 'sel' : False, 'color' : '#EED5B7', 'mbrs' : ['TITLE', 'NATIONALITY', 'RELIGION', 'CAUSE_OF_DEATH', 'CRIMINAL_CHARGE', 'URL']},

'SBJ' : {'ttype': 'DEP', 'sel' : True, 'color' : '#C1FF88', 'mbrs' : ['NSUBJ','NSUBJPASS']},
'OBJ' : {'ttype': 'DEP', 'sel' : True, 'color' : '#79A0F1', 'mbrs' : ['DOBJ']},
'APS' : {'ttype': 'DEP', 'sel' : True, 'color' : '#E3CF57', 'mbrs' : ['APPOS']},
'AMD' : {'ttype': 'DEP', 'sel' : True, 'color' : '#FF9912', 'mbrs' : ['AMOD']},
'CPD' : {'ttype': 'DEP', 'sel' : True, 'color' : '#00FFFF', 'mbrs' : ['COMPOUND']},
'MOD' : {'ttype': 'DEP', 'sel' : True, 'color' : '#FF69B4', 'mbrs' : ['NMOD:POSS','NEG','NMOD:TMOD','NUMMOD']},
'C-M' : {'ttype': 'DEP', 'sel' : False, 'color' : '#8FCC80', 'mbrs' : ['CASE', 'MARK']},
'CNJ' : {'ttype': 'DEP', 'sel' : False, 'color' : '#D8BFD8', 'mbrs' : ['CONJ']},
'*'   : {'ttype': 'DEP', 'sel' : False, 'color' : '#BFD8D8', 'mbrs' : ['DET','DET:PREDET','CC','CC:PRECONJ','AUX','AUXPASS','COP','PARATAXIS','MWE','EXPL','DISCOURSE']}
}

DEPLST = [y for x in tag_colors if tag_colors[x]['ttype'] == 'DEP' for y in tag_colors[x]['mbrs'] ]
revdeplst = [(y,x) for x in tag_colors if tag_colors[x]['ttype'] == 'DEP' for y in tag_colors[x]['mbrs']]
REVDEPD = {}
for itm in revdeplst: REVDEPD[itm[0]] = itm[1]

dcolr = '#FFFFFF'       # default text background color (white)

# ********************************** Definitions that enable hovering ***************************************

# ghost labels are invisible (since they same color as background) labels at upper left of tokens that allow hovering information
ghost_lbl_colr = '#F0F0F0'  # default color of ghost token labels in passage (used in hovering information) 
p_ghost_labels = []         # list containing passage ghost labels to enable hover info (destroyed when new passage is loaded)
q_ghost_labels = []         # list containing question ghost labels to enable hover info (destroyed when new question is loaded)
a_ghost_labels = []         # list containing question ghost labels to enable hover info (destroyed when new question is loaded)

# token dictionaries
psgtok_d = {}               # passage token dictionary: holds passage tokens data as output on storyCnv (some displayed on hover) 
segtok_d = {}               # sentence token dictionary: maps token in psgtok_d to sentence/sentence token
qtok_d = {}                 # question token dictionary: holds question tokens data as output on qarCnv (some displayed on hover)
atok_d = {}                 # answer token dictionary: holds answer tokens data as output on qarCnv (some displayed on hover)

# ********************************** Callback functions ***************************************

# callback for Ctrl-F (Find)
def ctrl_f(e):
   search_entry.focus() 


# callback for previous passage button
def p_prev_cb(e=None):
    global currpsg
    global currqar
    currpsg = (currpsg - 1) % len(coqa)
    currqar = 0
    show_passage(currpsg, currqar)


# callback for next passage button
def p_next_cb(e=None):
    global currpsg
    global currqar
    currpsg = (currpsg + 1) % len(coqa)
    currqar = 0
    show_passage(currpsg, currqar)


# callback for previous qar button
def qar_prev_cb(e=None):
    global currqar
    currqar = (currqar - 1) % len(coqa[currpsg]['q_tagged'])
    show_qar(currpsg, currqar)


# callback for next qar button
def qar_next_cb(e=None):
    global currqar
    currqar = (currqar + 1) % len(coqa[currpsg]['q_tagged'])
    show_qar(currpsg, currqar)


# callback for search entry box
def get_search_term(name, entry_w):
    srch_term = entry_w.get()
    if srch_term != "":
        if not scrollable or srch_term != search_term:
            search_for_term(srch_term)
        else:
            global scroll_idx
            scroll_idx = (scroll_idx + 1) % len(scrollable_lst)
            scroll_a_list()

    
# searches for a term (a string)
def search_for_term(tok):
    global search_fail_lbl
    global scrollable_lst
    global scroll_idx
    global scrollable
    global search_term
    search_term = tok
    search_results = []
    if search_fail_lbl:
        search_fail_lbl.destroy()
    search_toks = psgtok_d
    for i in search_toks:
        if tok.lower() in search_toks[i]['tok'].lower():
            search_results.append(('P', i))
    search_toks = qtok_d        
    for i in search_toks:
        if tok.lower() in search_toks[i]['tok'].lower():
            search_results.append(('Q', i))
    search_toks = atok_d
    for i in search_toks:
        if tok.lower() in search_toks[i]['tok'].lower():
            search_results.append(('A', i))
    if len(search_results) > 0:
        scrollable_lst = search_results
        scrollable = True
        scroll_idx = 0
        scroll_a_list()
    else:
        search_fail_lbl = Label(storyCnv, text='End reached. Text not found.', font="consolas 7 bold", anchor='nw', bg='red', borderwidth=0, justify=CENTER) # relief="solid")
        search_fail_lbl.place(x=1351,y=24)

            
# scroll through a list, highlighting the token at each element        
def scroll_a_list():
    global scroll_rect
    global scroll_cnv
    scroll_cnv.delete(scroll_rect)
    tup = scrollable_lst[scroll_idx]
    tokidx = tup[1]
    if tup[0] == 'P':
        toks_d = psgtok_d
        scroll_cnv = storyCnv
    else:
        scroll_cnv = qarCnv
        if tup[0] == 'Q': toks_d = qtok_d
        else: toks_d = atok_d
    tok = toks_d[tokidx]
    x1 = tok['x']
    y1 = tok['y']
    tlen = len(tok['tok'])
    scroll_rect = scroll_cnv.create_rectangle(x1-6, y1-4, x1+(tlen * FONT_W)+7, y1+18, width=4, outline='blue')


# clears scroll        
def clear_scrollable_cb(e):
    global scrollable
    scrollable = False
    search_entry.delete(0, END)
    storyCnv.delete(scroll_rect)
    qarCnv.delete(scroll_rect)
    if search_fail_lbl:
        search_fail_lbl.destroy()

# callback for scroll to previous
def scroll_prior_cb(event):
    global scroll_idx
    if scrollable:
        scroll_idx = (scroll_idx - 1) % len(scrollable_lst)
        scroll_a_list()


# callback for scroll to next
def scroll_next_cb(event):
    global scroll_idx
    if scrollable:
        scroll_idx = (scroll_idx + 1) % len(scrollable_lst)
        scroll_a_list()        
        

# callback for direct to passage entry box
def get_psg_entry(entry_w):
    p = entry_w.get()
    entry_w.delete(0, END)
    if p.isdigit():
        p = int(p)
        if p-1 < len(coqa):
            global currpsg
            global currqar
            currpsg = p - 1
            currqar = 0
            show_passage(currpsg, currqar)


# turn on hover text
def hover_on(lbl, name, ref, x, y):
    global hoverlbl
    if name == 'phover':
        P_X_MAX = 1499
        P_Y_MAX = 499
        tok_d = psgtok_d
        Cnv = storyCnv
    elif name == 'qhover' or name == 'ahover':
        P_X_MAX = 999
        P_Y_MAX = 249
        Cnv = qarCnv
        if name == 'qhover':
            tok_d = qtok_d
        else:
            tok_d = atok_d
    txtlst = []
    txtlst.append("POS: "+tok_d[ref]['pos'])
    if tok_d[ref]['lemma'] != '~': txtlst.append("lemma: "+tok_d[ref]['lemma'])
    if tok_d[ref]['ne'] != '-':
        if tok_d[ref]['ne'] == '<':
            i = 1
            while tok_d[ref-i]['ne'] == '<':
                i += 1
            txtlst.append("NE: "+tok_d[ref-i]['ne'])
        else:
            txtlst.append("NE: "+tok_d[ref]['ne'])
    if tok_d[ref]['deptype'] != '':
       txtlst.append("DEP: "+tok_d[ref]['deptype']+"("+tok_d[tok_d[ref]['dep_ref']]['tok']+")")

    txtlst.append("S"+str(tok_d[ref]['sent']+1)+"/W"+str(tok_d[ref]['s_tok']+1)+"/X"+str(tok_d[ref]['x'])+"/Y"+str(tok_d[ref]['y'])+"/L"+str(tok_d[ref]['line']))
    txt = '\n'.join(txtlst)
    w = max([len(s) for s in txtlst])
    h = len(txtlst)
    x = x + 5
    y = y + 12
    H_V_GAP = 15
    if x + w * FONT_W > P_X_MAX: x = P_X_MAX - w * FONT_W
    if y + h * (FONT_H + H_V_GAP) > P_Y_MAX: y -= h * (FONT_H + H_V_GAP)
    hoverlbl = Label(Cnv, text=txt, font=("consolas", 8), anchor='nw', bg='#FFFF00', relief=GROOVE, justify=LEFT)
    hoverlbl.place(x=x, y=y)


# turn off hover text
def hover_off(lbl):
    hoverlbl.destroy()


# handle checkbox for displaying rationale
def show_rationale_chk():
    show_passage(currpsg, currqar)


# handle checkbox for displaying coreferences
def show_coref_chk():
    global showDeps
    showDeps.set(False)
    show_passage(currpsg, currqar)


# handle checkbox for displaying dependency parse
def show_dep_chk():
    global showCorefs
    showCorefs.set(False)
    show_passage(currpsg, currqar)


# callback for changing color scheme
def tag_color_cb(k):  
    global lbltg
    if tag_colors[k]['sel'].get():
        lbltg = tag_colors[k]['ttype']
    show_passage(currpsg, currqar)
    

# displays transparent rectangle over text	
def alpha_rect(root, canvas, x1, y1, x2, y2, border, **kwargs):
    alpha = int(kwargs.pop('alpha') * 255)
    fill = kwargs.pop('fill')
    fill = root.winfo_rgb(fill) + (alpha,)
    image = Image.new('RGBA', (x2-x1, y2-y1), fill)
    alpha_image = ImageTk.PhotoImage(image)
    images['rationale'].append(alpha_image)
    canvas.create_image(x1, y1, image=images['rationale'][-1], anchor='nw', tags='alpha')
    if border:
        r = canvas.create_rectangle(x1, y1, x2, y2, **kwargs)
        return r


# draw curved lines between tokens (if straight lines are used, it's difficult to discern connection endpoints)
def link_toks(cnv, startx, starty, endx, endy, lcolor, arcit=False):

   midx = (startx + endx)/2      # midpoint x to create arc
   if arcit:
      midy = (starty + endy)/2      # midpoint y to create arc

      if midx < 750: midx = 375
      else: midx = 1125
      if midy < 250: midy = 125
      else: midy = 375

   else:
      midy = max(starty, endy) + 28

   cnv.create_line(startx, starty, midx, midy, endx, endy+FONT_H+4, arrow=LAST, fill=lcolor, smooth="true")


# output the current passage on the canvas   
def show_passage(pnum=0, qnum=0):

    tg = P_TAG                                  # Assume POS tags will be used for label colors
    if lbltg == 'NE':                           # Unless NE tags are called for
        tg = N_TAG

    d = coqa[pnum]                              # load passage from coqa in dictionary d

    storyCnv.delete("all")                      # clear all canvas items
    while p_ghost_labels:                       # clear all ghost labels 
        widget = p_ghost_labels.pop()
        widget.destroy()
    
    global search_term
    search_term = ""
    search_entry.delete(0, END)

    global scrollable
    scrollable = False
    
    storyCnv.create_text(100, 5, text=str(pnum+1)+' (News Story # '+str(d['story_num'])+')', font=("Arial", 14), anchor=NW)     # output the passage/story #

    psgtok_d.clear()
    segtok_d.clear()

    x = X_MIN                                       # x is token's x coordinate
    y = Y_MIN                                       # y is token's y coordinate

    line_num = 1
    tok_cnt = 0
    pdeps = []

    
    for i in range(len(d['seg_tagged'])):           # i is each tagged sentence
        sg = d['seg_tagged'][i]                     # sg is the tagged sentence being processed
        #print(d['seg_dep'][i])
        deps = [(dep[0], dep[1], dep[2]) for dep in d['seg_dep'][i]]  # (1-based) index0 is dependency type, index1 is token index receiver of dependency, index2 token index of dependency 
        depd = {}
        rootdep = -1
        for dep in deps:
           if dep[0] != 'ROOT':
              depd[dep[2]-1] = (dep[0].upper(),dep[1]-1)        # ensure 0-based token indices are stored
           else:
              rootdep = dep[2]-1
              
        for j in range(len(sg)):                    # j is each token tuple index in sg
            segtok_d[(i,j)] = tok_cnt
            tok_d = {}
            tok = sg[j][TOK]                       # tok is the jth token
            tlen = len(tok)                         # tlen is token's length in characters           
            glen = W_GAP * FONT_W                   # glen is the gap that precedes the token (in pixels)
            outlen = tlen * FONT_W                  # outlen is the token's length in pixels
            if x + (W_GAP + tlen) * FONT_W >= X_MAX:# text exceeds X_MAX (right screen margin), so wrap 
                x = X_MIN
                y += V_GAP
                line_num += 1
            elif x > X_MIN:                         # only precede token by gap if it is not the first token in the line
                x += glen

            if sg[j][tg] == '<':
               sg[j][tg] = sg[j-1][tg]              # "Fixes" preprocessed data by expanding previously collapsed token tag (<)
            toktag = sg[j][tg]                      # extract the tag that will be used for label color
                                 

            # load the token's output (on storyCnv) info: sentence it came, token in sentence, x and y coords, line it was output on
            tok_d['tok'] = tok
            tok_d['s_map'] = sg[j][M_TAG]
            tok_d['pos'] = sg[j][P_TAG]
            tok_d['ne'] = sg[j][N_TAG]
            tok_d['lemma'] = sg[j][L_TAG]
            tok_d['sent'] = i
            tok_d['s_tok'] = j
            tok_d['x'] = x
            tok_d['y'] = y
            tok_d['line'] = line_num
            if j in depd and depd[j][0] in DEPLST:          # if tag is a member of the selected highlighting (the split[0] is for NE tags)
                  tok_d['deptype'] = depd[j][0]
                  tok_d['dep_ref'] = tok_cnt+(depd[j][1]-j)
                  pdeps.append((depd[j][0], tok_cnt, tok_cnt+(depd[j][1]-j)))
            else:
               tok_d['deptype'] = ""
               tok_d['dep_ref'] = ""


            # Code below select the label color for the token
            colr = dcolr                              # Tokens not having tags of interest are output with default label color

            if lbltg != 'DEP':
               for tagk in tag_colors:                 # Search for the correct color (it's a many to one (color) mapping
                  if tag_colors[tagk]['ttype'] == lbltg and tag_colors[tagk]['sel'].get():    # if right label and checked for viewing
                     if toktag.split()[0] in tag_colors[tagk]['mbrs']:          # if tag is a member of the selected highlighting (the split[0] is for NE tags)
                        colr = tag_colors[tagk]['color']            # store its color value
                        break
            else:
               for tagk in tag_colors:                 # Search for the correct color (it's a many to one (color) mapping
                     if tag_colors[tagk]['ttype'] == lbltg and tag_colors[tagk]['sel'].get():    # if right label and checked for viewing
                        if j in depd and depd[j][0] in tag_colors[tagk]['mbrs']:          # if tag is a member of the selected highlighting (the split[0] is for NE tags)
                           colr = tag_colors[tagk]['color']            # store its color value
                           break
     
               
            # output ghost label in upper left corner of label to enable hovering information, and append ghost label to list
            lbl = Label(storyCnv, text='', font=("consolas", 1), anchor='nw', bg=ghost_lbl_colr) #, borderwidth=1, relief="solid")
            lbl.bind("<Enter>", lambda name='pghost', ref=tok_cnt, x=x, y=y : hover_on(lbl, 'phover', ref, x, y))
            lbl.bind("<Leave>", lambda name='pghost': hover_off(lbl))
            lbl.place(x=x-8, y=y)
            p_ghost_labels.append(lbl)

            # output the (colorized) token
            storyCnv.create_rectangle(x-2, y, x+outlen+2, y+FONT_H+5, outline="#000", fill=colr)
            if j == rootdep: storyCnv.create_rectangle(x-3, y-2, x+outlen+4, y+FONT_H+7, width=3, outline="#000")
            storyCnv.create_text(x, y, text=tok, font=("consolas", 8), anchor='nw')

            
            psgtok_d[tok_cnt] = tok_d                  # append the tokens dictionary to the passage dictionary

            x += (W_GAP + tlen) * FONT_W            # update the x pixel coordinate
   
            tok_cnt += 1                            # increment the (passage) token counter


    if showCorefs.get():

       crefcolr = 0
       for k in d['corefs']:                          # k is the key to a single set of coreferences (refs to same entity)
          references = []                             # this will store the referring tokens
          for ref in d['corefs'][k]:                  # ref is an individual coref in k
             sentnum = ref['sentNum']
             toknum = ref['startIndex']
             if ref['repmention']:
               referent = segtok_d[(sentnum,toknum)]
             else:         
               references.append(segtok_d[(sentnum,toknum)])
          endx = psgtok_d[referent]['x']
          endy = psgtok_d[referent]['y']
          for ref in references:
            startx = psgtok_d[ref]['x']
            starty = psgtok_d[ref]['y']

            crefcolr = (crefcolr + 1) % len(coref_colors)

            link_toks(storyCnv, startx, starty, endx, endy, coref_colors[crefcolr], arcit=True)

    if showDeps.get():
      for dep in pdeps:
         dtype = dep[0] # dependency type
         t1 = dep[1]    # token 1 (from)
         t2 = dep[2]    # token 2 (to)
         if tag_colors[REVDEPD[dtype]]['sel'].get():
            startx = psgtok_d[t1]['x']
            starty = psgtok_d[t1]['y'] + FONT_H + 6
            endx = psgtok_d[t2]['x']
            endy = psgtok_d[t2]['y']
            link_toks(storyCnv, startx, starty, endx, endy, "#DC143C")
              
    show_qar(pnum, qnum)                                  # call function to output the question/answer



# output the current question/answer/rationale on the qar canvas
def show_qar(pnum=0, qnum=0):
    tg = P_TAG                                  # Assume POS tags will be used for label colors
    if lbltg == 'NE':                           # Unless NE tags are called for
        tg = N_TAG

    global scrollable
    scrollable = False

    global seg_scores_list
    
    qarCnv.delete("all")                            # clear the qar canvas
    qtok_d.clear()
    atok_d.clear()

    while q_ghost_labels:                           # clear all question ghost labels 
        widget = q_ghost_labels.pop()
        widget.destroy()

    while a_ghost_labels:                           # clear all answer ghost labels 
        widget = a_ghost_labels.pop()
        widget.destroy()

    images['rationale'].clear()                     # clear all rationale highlights
    
    d = coqa[pnum]                                  # load entire passage from coqa
    
    qarCnv.create_text(98, 10, text=str(qnum+1), font=("Arial", 14)) # output question number
   
    qs = d['q_tagged'][qnum]                        # load the tagged question from coqa

    x = X_MIN                                       # x is token's x coordinate
    y = Q_Y_MIN                                     # y is token's y coordinate
    qline_num = 1

    pdeps = []

    deps = [(dep[0], dep[1], dep[2]) for dep in d['q_dep'][qnum]]  # (1-based) index0 is dependency type, index1 is token index receiver of dependency, index2 token index of dependency 
    depd = {}
    rootdep = -1
    for dep in deps:
      if dep[0] != 'ROOT':
         depd[dep[2]-1] = (dep[0].upper(),dep[1]-1)        # ensure 0-based token indices are stored
      else:
         rootdep = dep[2]-1


    for j in range(len(qs)):                        # j is the index of each token tuple
        qtoks = {}
        q = qs[j]                                   # q is the entire token tuple
        tok = q[TOK]                                # tok is the token
        tlen = len(tok)                             # tlen is token's length in characters 
        glen = W_GAP * FONT_W                       # glen is the gap that precedes the token (in pixels)
        outlen = tlen * FONT_W                      # outlen is the token's length in pixels
        if x + (W_GAP + tlen) * FONT_W >= Q_X_MAX:  # text exceeds Q_X_MAX (right screen margin), so wrap 
            x = X_MIN
            y += V_GAP
            qline_num += 1
        elif x > X_MIN:                             # only precede token by gap if it is not the first token in the line
            x += glen

        colr = dcolr                            # Tokens not having tags of interest are output with default label color

        if qs[j][tg] == '<':
            qs[j][tg] = qs[j-1][tg]              # "Fixes" preprocessed data by expanding previously collapsed token tag (<)
        toktag = qs[j][tg]                      # extract the tag that will be used for label color
                              
        qtoks['tok'] = tok
        qtoks['pos'] = q[P_TAG]
        qtoks['ne'] = q[N_TAG]
        qtoks['lemma'] = q[L_TAG]
        qtoks['sent'] = 0
        qtoks['s_tok'] = j
        qtoks['x'] = x
        qtoks['y'] = y
        qtoks['line'] = qline_num
        if j in depd and depd[j][0] in DEPLST:          # if tag is a member of the selected highlighting (the split[0] is for NE tags)
            qtoks['deptype'] = depd[j][0]
            qtoks['dep_ref'] = depd[j][1]
            pdeps.append((depd[j][0], j, depd[j][1]))
        else:
           qtoks['deptype'] = ""
           qtoks['dep_ref'] = ""

        qtok_d[j] = qtoks
        

        if lbltg != 'DEP':
           for tagk in tag_colors:                 # Search for the correct color (it's a many to one (color) mapping
            if tag_colors[tagk]['ttype'] == lbltg and tag_colors[tagk]['sel'].get():    # if right label and checked for viewing
                if toktag.split()[0] in tag_colors[tagk]['mbrs']:          # search all tags that use the particular color
                    colr = tag_colors[tagk]['color']            # and store its value
                    break
        else:
            for tagk in tag_colors:                 # Search for the correct color (it's a many to one (color) mapping
               if tag_colors[tagk]['ttype'] == lbltg and tag_colors[tagk]['sel'].get():    # if right label and checked for viewing
                  if j in depd and depd[j][0] in tag_colors[tagk]['mbrs']:          # if tag is a member of the selected highlighting (the split[0] is for NE tags)
                     colr = tag_colors[tagk]['color']            # store its color value
                     break
           

      
        # output ghost label to enable hovering information, and append ghost label to list
        lbl = Label(qarCnv, text='', font=("consolas", 1), anchor='nw', bg=ghost_lbl_colr) #, borderwidth=1, relief="solid")
        lbl.bind("<Enter>", lambda name='qghost', ref=j, x=x, y=y : hover_on(lbl, 'qhover', ref, x, y))
        lbl.bind("<Leave>", lambda name='qghost': hover_off(lbl))
        lbl.place(x=x-8, y=y)
        q_ghost_labels.append(lbl)

        # output the (colorized) token
        qarCnv.create_rectangle(x-2, y, x+outlen+2, y+FONT_H+5, outline="#000", fill=colr)
        if j == rootdep: qarCnv.create_rectangle(x-3, y-2, x+outlen+4, y+FONT_H+7, width=3, outline="#000")
        qarCnv.create_text(x, y, text=tok, font=("consolas", 8), anchor='nw')

        x += (W_GAP + tlen) * FONT_W                # update the x pixel coordinate



    ans = d['a_tagged'][qnum]                       # load the tagged answer from coqa

    x = X_MIN                                       # x is token's x coordinate
    y = A_Y_MIN                                     # y is token's y coordinate
    aline_num = 1    
    for j in range(len(ans)):                       # j is the index of each token tuple
        atoks = {}
        a = ans[j]                                  # a is the entire token tuple
        tok = a[TOK]                                # tok is the token
        tlen = len(tok)                             # tlen is token's length in characters 
        glen = W_GAP * FONT_W                       # glen is the gap that precedes the token (in pixels)
        outlen = tlen * FONT_W                      # outlen is the token's length in pixels
        if x + (W_GAP + tlen) * FONT_W >= Q_X_MAX:  # text exceeds Q_X_MAX (right screen margin), so wrap
            x = X_MIN
            y += V_GAP
            aline_num += 1
        elif x > X_MIN:                             # only precede token by gap if it is not the first token in the line
            x += glen

        colr = dcolr                               # Tokens not having tags of interest are output with default label color


        if ans[j][tg] == '<':
            ans[j][tg] = ans[j-1][tg]              # "Fixes" preprocessed data by expanding previously collapsed token tag (<)
        toktag = ans[j][tg]                        # extract the tag that will be used for label color
                              
        for tagk in tag_colors:                    # Search for the correct color (it's a many to one (color) mapping
            if tag_colors[tagk]['ttype'] == lbltg and tag_colors[tagk]['sel'].get():    # if right label and checked for viewing
                if toktag.split()[0] in tag_colors[tagk]['mbrs']:          # search all tags that use the particular color
                    colr = tag_colors[tagk]['color']            # and store its value
                    break

        # output ghost label to enable hovering information, and append ghost label to list
        lbl = Label(qarCnv, text='', font=("consolas", 1), anchor='nw', bg=ghost_lbl_colr) #, borderwidth=1, relief="solid")
        lbl.bind("<Enter>", lambda name='aghost', ref=j, x=x, y=y : hover_on(lbl, 'ahover', ref, x, y))
        lbl.bind("<Leave>", lambda name='aghost': hover_off(lbl))
        lbl.place(x=x-8, y=y)
        a_ghost_labels.append(lbl)

        # output the (colorized) token
        qarCnv.create_rectangle(x-2, y, x+outlen+2, y+FONT_H+5, outline="#000", fill=colr)
        qarCnv.create_text(x, y, text=tok, font=("consolas", 8), anchor='nw')

        atoks['tok'] = tok
        atoks['pos'] = a[P_TAG]
        atoks['ne'] = a[N_TAG]
        atoks['lemma'] = a[L_TAG]
        atoks['sent'] = 0
        atoks['s_tok'] = j
        atoks['x'] = x
        atoks['y'] = y
        atoks['line'] = aline_num
        atoks['deptype'] = ""
        atoks['dep_ref'] = ""

        atok_d[j] = atoks
        
        x += (W_GAP + tlen) * FONT_W                # update the x pixel coordinate


    if showRationale.get():
        # highligh rationale given for answer - remove leading/trailing punctuation and whitespace
        r_start = d['rationale'][qnum][0]          
        r_end = d['rationale'][qnum][1]
        span = d['story'][r_start:r_end]                # original rationale span
        blen = len(span)                                # get span length
        span = span.lstrip(' \t\n,.:')                  # remove leading undesired
        alen = len(span)                                # get (possibly) new length
        r_start += blen - alen                          # adjust span start by leading removed (if any)
        span = span.rstrip(' \t\n,.:')                  # remove trailing undesired
        blen = len(span)                                # get (possibly) new length
        r_end -= alen - blen                            # adjust span end by trailing removed (if any)
        span = d['story'][r_start:r_end]                # get "cleaned" span

        f_tok = -1
        l_tok = -1
        for k in range(len(psgtok_d)):
            if int(psgtok_d[k]['s_map']) >= r_start:
                break

        if int(psgtok_d[k]['s_map']) > r_start and k > 0:
            f_tok = k - 1
        elif int(psgtok_d[k]['s_map']) == r_start:
            f_tok = k
        else:
            print("Error did not find start token!")

        if len(span) > len(psgtok_d[f_tok]['tok']): 
            for k in range(f_tok, len(psgtok_d)):
                if int(psgtok_d[k]['s_map']) >= r_end:
                    break
            l_tok = k - 1
        else:
            l_tok = f_tok
        
        f_line = psgtok_d[f_tok]['line']                   # get first line (on canvas) of span
        l_line = psgtok_d[l_tok]['line']                   # get last line (on canvas) of span
                    
        # highlingt first line of rationale span
        x1 = psgtok_d[f_tok]['x']
        if x1 == X_MIN:
            x1 = X_MIN - 10                             # if it begins at the start of canvas line, add a border to left
        else:
            x1 -= W_GAP * FONT_W                                # otherwise slightly pad the highlingh on the left
        if l_tok < len(psgtok_d) - 1 and psgtok_d[l_tok+1]['line'] != f_line:
            x2 = X_MAX + 10                             # if first will span to right margin, add border
        else:
             x2 = psgtok_d[l_tok]['x'] + (len(psgtok_d[l_tok]['tok'])+2) * FONT_W     # otherwise pad last token on the right
        y1 = psgtok_d[f_tok]['y'] - V_GAP//3               # pad highlight above token
        y2 = psgtok_d[f_tok]['y'] + FONT_H + V_GAP//2      # pad highlight below token

        alpha_rect(root, storyCnv, x1, y1, x2, y2, False, fill='orange', alpha=.3)

        # highlight last line of rationale, when there are at least two lines to be highlighted    
        if l_line != f_line:
            x1 = X_MIN - 10                             # last line (of multi-line) always begins at left margin
            if l_tok < len(psgtok_d) - 1 and psgtok_d[l_tok+1]['line'] != l_line:
                #print("DIFF")
                x2 = X_MAX + 10                         # if first will span to right margin, add border
            else:
                 x2 = psgtok_d[l_tok]['x'] + (len(psgtok_d[l_tok]['tok'])+1) * FONT_W # otherwise pad last token on the right
            y1 = psgtok_d[l_tok]['y'] - V_GAP//3                                   # pad highlight above token
            y2 = psgtok_d[l_tok]['y'] + FONT_H + V_GAP//2                          # pad highlight below token
            alpha_rect(root, storyCnv, x1, y1, x2, y2, False, fill='orange', alpha=.3)

        # highlight rationales that span more than 2 lines (from line after the first to the line before the last)
        if l_line - f_line > 1:
            x1 = X_MIN - 10                                                     # the "betweens" are always full lines - start at left
            x2 = X_MAX + 10                                                     # and go to the right margin
            y1 = psgtok_d[f_tok]['y'] + FONT_H + V_GAP//2 + 1                      # y1 begins immediately after first line
            y2 = psgtok_d[l_tok]['y'] - V_GAP//3                                   # y2 ends immediately before last line                    
            alpha_rect(root, storyCnv, x1, y1, x2, y2, False, fill='orange', alpha=.3)
        
    if showDeps.get():
      for dep in pdeps:
         dtype = dep[0] # dependency type
         t1 = dep[1]    # token 1 (from)
         t2 = dep[2]    # token 2 (to)
         if tag_colors[REVDEPD[dtype]]['sel'].get():
            startx = qtok_d[t1]['x']
            starty = qtok_d[t1]['y'] + FONT_H + 6
            endx = qtok_d[t2]['x']
            endy = qtok_d[t2]['y']
            link_toks(qarCnv, startx, starty, endx, endy, "#DC143C")

    # remove the old span scores (rankings) for the question from the story/passage board
    for itm in seg_scores_list:
       storyCnv.delete(itm)
    seg_scores_list.clear()

    # output the span scores/rankings for this question
    segscores = get_seg_scores(pnum,qnum)
    segscores = sorted(segscores,key=lambda x: x[1],reverse=True)
    
    rank = 1       
    for itm in segscores:
       snum = itm[0]
       qscore = format(itm[1],'.3f')
       tok = segtok_d[(snum,0)]
       fcolor = 'black'
       txt = '#'+str(rank)+'  '+qscore
       x = psgtok_d[tok]['x']
       y = psgtok_d[tok]['y']
       if rank == 1:
          fcolor = 'red'
          seg_scores_list.append(storyCnv.create_rectangle(x-10, y-12, x+30, y-1, fill='yellow', outline=""))
       seg_scores_list.append(storyCnv.create_text(x-10, y-12, text=txt, font=("Arial 7"), anchor='nw', fill=fcolor)) 
       rank += 1

 
# loads the (externally generated) scores for individual sentences 
def load_scores_dict():
   with open('sentence-scores.txt','r') as ff:
      sdict = {}                                              # scores dictionary
      for line in ff:
         line = line.split()
         pqs = line[0].split('.')
         pnum = int(pqs[0])
         qnum = int(pqs[1])
         segnum = int(pqs[2])
         segscore = float(line[1])
         if pnum not in sdict:
            sdict[pnum] = {}
         if qnum not in sdict[pnum]:
            sdict[pnum][qnum] = []

         sdict[pnum][qnum].append((segnum,segscore))

   return sdict


# returns (a copy) of the list of sentence scores from the scores dictionary for the passage (pnum)/question(num)
# the copy preserves original list since returned value is manipulated
def get_seg_scores(pnum,qnum):
   return([] + scores_dict[pnum][qnum])


def main():
    #test_it()

    show_passage(currpsg)

    root.mainloop()



lbltg = "DEP"                   # Default to using DEP (dependency parse) tags for label colors


root = Tk()
root.title("CoQA News Viz")
root.geometry("1532x795+0+0")   # 1532x795 max on my screen
root.resizable(0,0)

top = Frame(root, borderwidth=2, relief="solid")
bottom = Frame(root, borderwidth=2, relief="solid")

left = Frame(bottom, borderwidth=2, relief="solid")
right = Frame(bottom, borderwidth=2, relief="solid")
storyCnv = Canvas(top, width=1500, height=500)
qarCnv = Canvas(left, width=1000, height=250)
ctrlCnv = Canvas(right, width=500, height=250)

top.pack(padx=5, pady=5)
bottom.pack(fill="both")
left.pack(side="left", padx=5, pady=5)
right.pack(side="right", expand=True, fill="both", padx=5, pady=5)
storyCnv.pack()
qarCnv.pack()
ctrlCnv.pack()


psgLabel = Label(storyCnv, text="Passage:", font=("Arial", 14))
psgLabel.place(x=2, y=2)                 
searchLabel = Label(storyCnv, text="Find", font="Arial 10 bold", fg='IndianRed4')
searchLabel.place(x=1310, y=2)                 
search_entry = Entry(storyCnv,width=20, font=("Arial",10), justify=LEFT)
search_entry.place(x=1350,y=3)
search_entry.bind("<Return>", lambda event : get_search_term('search', search_entry))


qLabel = Label(qarCnv, text="Question", font=("Arial", 14))
qLabel.place(x=2, y=Q_Y_MIN - 30)                       

aLabel = Label(qarCnv, text="Answer", font=("Arial", 14))
aLabel.place(x=2, y=A_Y_MIN - 30)                 

with open('coqa-news-preprocessed-final.json', 'r', encoding='utf-8') as read_file:
   coqa = json.load(read_file)
   coqa = coqa['data']

scores_dict = load_scores_dict()
	
qmap = {}

currpsg = 0    # current passage (story) being displayed
currqar = 0    # current question/answer/rationale (in above passage) being displayed

# Go direct to a passage entry box
ctrlCnv.create_text(5, 3, text='Go to Passage #', font=("consolas", 10), anchor='nw', fill='IndianRed4')
passage_entry = Entry(ctrlCnv,width=7, justify=CENTER)
passage_entry.place(x=35,y=18)
passage_entry.bind("<Return>", lambda name='gotopassage': get_psg_entry(passage_entry))

# load icons for previous and next buttons
pPrev_img = PhotoImage(file="prev.png")
images['pPrev'] = pPrev_img
pNext_img = PhotoImage(file="next.png")
images['pNext'] = pNext_img
qPrev_img = PhotoImage(file="up.png")
images['qPrev'] = qPrev_img
qNext_img = PhotoImage(file="down.png")
images['qNext'] = qNext_img

# Passage previous and next
ctrlCnv.create_text(33, 44, text='Passage', font=("consolas", 10), anchor='nw')
btnPprev = Button(ctrlCnv,command=p_prev_cb)
btnPprev.config(image=images['pPrev'],width="14",height="14")
btnPprev.place(x=5,y=42)
btnPnext = Button(ctrlCnv,command=p_next_cb)
btnPnext.config(image=images['pNext'],width="14",height="14")
btnPnext.place(x=90,y=42)

# Question previous and next    
ctrlCnv.create_text(30, 73, text='Question', font=("consolas", 10), anchor='nw')
btnQprev = Button(ctrlCnv,command=qar_prev_cb)
btnQprev.config(image=images['qPrev'],width="14",height="14")
btnQprev.place(x=5,y=72)    
btnQnext = Button(ctrlCnv,command=qar_next_cb)
btnQnext.config(image=images['qNext'],width="14",height="14")
btnQnext.place(x=90,y=72)

# Highlight POS tags in color
posColorFrame = LabelFrame(ctrlCnv, text="Part-of-Speech Tags")
posColorFrame.place(x=120, y=3)

# Highlight NE tags in color
neColorFrame = LabelFrame(ctrlCnv, text="Named-Entity Types")
neColorFrame.place(x=120, y=50)

# Highlight DEP tags in color
depColorFrame = LabelFrame(ctrlCnv, text="Dependency Parse")
depColorFrame.place(x=5, y=97)

# Choose correct set of label highlighting (POS tags, NE tags, or Dependency parse tags)
for k in tag_colors:                         # K is each displayed tag
    #print(k)
    frm = depColorFrame                      # Initialize POS frame to update below
    tag_colors[k]['sel'] = BooleanVar()      # Check the tag for selection
    if tag_colors[k]['ttype'] == 'DEP':      # if it's a POS checkbox
        tag_colors[k]['sel'].set(True)       # make it active
    elif tag_colors[k]['ttype'] == 'NE':     # if it's an NE checkbox
        tag_colors[k]['sel'].set(False)      # make it inactive
        frm = neColorFrame                   # and select its frame to update below
    elif tag_colors[k]['ttype'] == 'POS':    # if it's an NE checkbox
        tag_colors[k]['sel'].set(False)      # make it inactive
        frm = posColorFrame                  # and select its frame to update below
    tag_colors[k]['chkbox'] = Checkbutton(frm, text=k, variable=tag_colors[k]['sel'], bg=tag_colors[k]['color'], command=(lambda k=k: tag_color_cb(k)))
    tag_colors[k]['chkbox'].pack(side=LEFT)
                      
# Choose whether to highlight the rationale
showRationale = BooleanVar()
showRationale.set(True)
rationaleFrame = LabelFrame(ctrlCnv, text="Rationale")
rationaleFrame.place(x=430, y=3)
rationaleChkBtn = Checkbutton(rationaleFrame, text="Show", var=showRationale, command=(lambda : show_rationale_chk()))
rationaleChkBtn.pack(side=LEFT)
rationaleChkBtn.select()

# Choose whether to display coreferences
showCorefs = BooleanVar()
showCorefs.set(False)
corefFrame = LabelFrame(ctrlCnv, text="Corefs")
corefFrame.place(x=432, y=50)
corefChkBtn = Checkbutton(corefFrame, text="Show", var=showCorefs, command=(lambda : show_coref_chk()))
corefChkBtn.pack(side=LEFT)

# Choose whether to display dependency links
showDeps = BooleanVar()
showDeps.set(False)
defFrame = LabelFrame(ctrlCnv, text="Deps")
defFrame.place(x=432, y=97)
defChkBtn = Checkbutton(defFrame, text="Show", var=showDeps, command=(lambda : show_dep_chk()))
defChkBtn.pack(side=LEFT)

hoverlbl = Label(storyCnv, text='sup', font=("consolas", 8), anchor='nw', bg='magenta') #, borderwidth=1, relief="solid")
hoverlbl.pack_forget()

scroll_idx = 0
scrollable_lst = []
scroll_cnv = storyCnv
scrollable = False
search_term = ""
search_fail_lbl = Label(storyCnv, text='End reached. Text not found.', font="consolas 7 bold", anchor='nw', bg='red', borderwidth=0, justify=CENTER) # relief="solid")
scroll_rect = storyCnv.create_rectangle(0,0,0,0)    # bogus rectangle so we get global variable 

# bind callback functions to handle keys
root.bind('<Prior>', scroll_prior_cb)
root.bind('<Shift-F3>', scroll_prior_cb)
root.bind('<Next>', scroll_next_cb)
root.bind('<F3>', scroll_next_cb)
root.bind('<Left>', p_prev_cb)
root.bind('<Right>', p_next_cb)
root.bind('<Up>', qar_prev_cb)
root.bind('<Down>', qar_next_cb)
root.bind('<Escape>', clear_scrollable_cb)
root.bind('<Control-f>', ctrl_f)

seg_scores_list = []

main()
