/*
 * match.c
 *
 *  Created on: Mar 20, 2013
 *      Author: James Mcclain, Antonis Kalou
 */
/* This program is free software: you can redistribute it and/or modify */
/* it under the terms of the GNU General Public License as published by */
/* the Free Software Foundation, either version 3 of the License, or */
/* (at your option) any later version. */

/* This program is distributed in the hope that it will be useful, */
/* but WITHOUT ANY WARRANTY; without even the implied warranty of */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the */
/* GNU General Public License for more details. */

/* You should have received a copy of the GNU General Public License */
/* along with this program.  If not, see <http://www.gnu.org/licenses/>. */

// Find errors or debug code by searching DEBUG

// The code is a little messy, a dictionary 2.0 would
// be separated into files instead of one big one.
// But it could be worse.

// (c) James McClain <jamezmcclain@gmail.com>

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "match.h"
#include "commands.h"

// PROTOTYPES *******************

int check_equality(char *speech,char *buffer,struct config *cfg);
int any_match(char **buffer,char **speech,char start,char end,struct config *cfg);
int any_atomic_match(char **buffer,char **speech,char start,char end,struct config *cfg);
char *line_match(char *buf,char **tmpSpeech,struct config *cfg);

//********************************


// square bracket match
int sb_match(char **buffer,char **speech,struct config *cfg) {
  return any_match(buffer,speech,'[',']',cfg);
}

// less than match
int lt_match(char **buffer,char **speech,struct config *cfg) {
  return any_match(buffer,speech,'<','>',cfg);
}

// bracket (variable) match.
// Matches the syntax: ( WORD varname )   or  ( LINE varname [optional stopping expression] )
int op_match(char **buffer,char **speech,struct config *cfg) {

  char *buf = *buffer;
  char *tmpSpeech = *speech;

  if(*buf != '(') {
    printf("Incorrect used of op_match, **buffer != '('\n");
    exit(1);
  }

  ++buf;
  char *startVarName = buf;
  char *lineSpeech = NULL;
  while(*buf != ' ' &&	*buf != '\0' && *buf != '\n' &&
  	*buf != '\r' &&	*buf != '<') {

    ++buf;
  }


  if(*buf == '\0' || *buf == '\n' || *buf == '\r') {
    printf("Incorrect syntax in op_match!\n");
    exit(1);
  }
  char saveChar = *buf;
  *buf = '\0';


  if(strcmp(startVarName,"WORD") == 0) {
    *buf = saveChar;
    if(*buf == '<') {
      lt_match(&buf,&tmpSpeech,cfg);
    } else {
      while(*tmpSpeech != ' ' && *tmpSpeech != '\n' &&
	     *tmpSpeech != '\r' && *tmpSpeech != '\0') {
	       ++tmpSpeech;
      }
    }
  } else if(strcmp(startVarName,"LINE") == 0) {
    // solution, make Line in this format
    // (Line varname Match Until this)
    // With Match Until this being everything until the
    // ), with ( not allowed.
    // nothing there or just spaces simply means to match
    // until the end of the line.
    *buf = saveChar;
    if(*buf == '<') {
      lt_match(&buf,&tmpSpeech,cfg);
    } else {
      // buf won't change, but tmpSpeech must.
      lineSpeech = line_match(buf,&tmpSpeech,cfg);
    }
  }
  else {
    printf("%s is not a variable name or is not "
	   "implemented.\n",startVarName);
    exit(1);
  }


  if( !cfg->store_variables || !(tmpSpeech > *speech)) {
    while(*buf != ')' && *buf != '\n' && *buf != '\0' && *buf != '\r') {
      ++buf;
    }
    if(*buf != ')') {
      printf("Error in syntax of op_match()!\n");
      exit(1);
    }
    ++buf;
    *buffer = buf;
  } else {
    //get the variable name.
    //reusing startVarName

    if(cfg->var_LL->next != NULL) {
      printf("var_LL->next is not NULL!\n");
      exit(1);
    }

    cfg->var_LL->next = malloc(1*sizeof(struct variables));
    if(cfg->var_LL->next == NULL) {
      printf("Memory Error in op_match!\n");
      exit(1);
    }
    cfg->var_LL = cfg->var_LL->next;

   while(*buf == ' ') {
    	++buf;
    }
    if(*buf == ')') {
      printf("Incorrect syntax in op_match()!\n");
      exit(1);
    }
    startVarName = buf;
    while(*buf != ' ' && *buf != ')') {
      if(*buf == '$') {
      	printf("Error, can't have $ in a varname!\n");
      	exit(1);
      }
      ++buf;
    }
    saveChar = *buf;
    *buf = '\0';
    cfg->var_LL->varName = malloc(sizeof(char)*strlen(startVarName)+1);

    if(cfg->var_LL->varName == NULL) {
      printf("Memory error in op_match!\n");
      exit(1);
    }
    strcpy(cfg->var_LL->varName,startVarName);
    *buf = saveChar;
    while(*buf != ')' && *buf != '\n' && *buf != '\0' && *buf != '\r') {
      ++buf;
    }
    if(*buf != ')') {
      printf("Error in syntax of op_match()!\n");
      exit(1);
    }
    ++buf;
    *buffer = buf;
    cfg->var_LL->next = NULL;

  } if(tmpSpeech > *speech) { // A match!
    if(cfg->store_variables) {
      saveChar = *tmpSpeech;
      *tmpSpeech = '\0';
      cfg->var_LL->varValue = malloc(sizeof(char)*strlen(*speech)+1);

      if(cfg->var_LL->varValue == NULL) {
      	printf("MEMORY error in op_match!\n");
      	exit(1);
      }
      strcpy(cfg->var_LL->varValue,*speech);
      *tmpSpeech = saveChar;
    }
    if(!lineSpeech) {
      *speech = tmpSpeech;
    }
    else {
      *speech = lineSpeech;
    }
    return 1;
  }
  return 0;
}

/**
* Generic parenthesis matcher.
* Return true if the current line of dictionary (/buffer/) begins with a valid block of parenthesis (/start/ and /end/),
* and the current /speech/ matches such a block.
* Then, moves both the pointers after the match. 
* Notice:
* 1. /buffer/ must begin with /start/ char.
* 2. The function is recursive, thus it handles different kinds of parenthesis: []  <>  ()
* 3. The function starts with the following control: expression is ok iff it contains a good number of /start/ and /end/ parenthesis.
*    This control, IMO, does not check the different kinds of parenthesis.
*/
int any_match(char **buffer,char **speech,char start,char end,struct config *cfg) {

  if(**buffer != start) {
    printf("ERROR, any_match() called, but **buffer != '%c'\n",
	   start);

    exit(1);
  }
  ++(*buffer);
  //printf("matching buf='%s' speech='%s'\n", *buffer, *speech); //DEBUG

  char *buf = *buffer;
  char *Gspeech = *speech;    //final position for *speech
  char *tmpSpeech = *speech;  //current position in speech

  int stop = 1;

  while(stop != 0) { // While we are in a balanced expression.
    if(**buffer == '\n' || **buffer == '\0' || **buffer == '\r') {
      printf("ERROR, incorrect syntax of %c%c\n",start,end);
      exit(1);
    }
    if(**buffer == start) {
      ++stop;
    }
    if(**buffer == end) {
      --stop;
    }
    ++(*buffer);
    if(**buffer == '\\') {
      // Not sure about the flows of these ifs
      ++(*buffer);
      if(**buffer != '\0')
	     ++(*buffer);
    }
  }
  --(*buffer);
  // We are now at the matching > or ]
  //HERE: buf points at beginning of pattern
  //      *buffer points at end of patter
  //      *speech,tmpSpeech,Gspeech point at beginning of speech

  while(buf != *buffer) {
    if(*buf == ',') {
      if(tmpSpeech > Gspeech) {
      	Gspeech = tmpSpeech;
      	tmpSpeech = *speech;
      }
      ++buf;
    }
    if(*buf == '<') {
      if(! lt_match(&buf,&tmpSpeech,cfg)) {
      	tmpSpeech = *speech;

      	while(!(buf == *buffer || *buf == ',')) {
      	  ++buf;
      	}
      }
      continue;
    }
    if(*buf == '(') {
      if(! op_match(&buf,&tmpSpeech,cfg)) {
      	tmpSpeech = *speech;

      	while(!(buf == *buffer || *buf == ',')) {
      	  ++buf;
      	}
      }
      continue;
    }

    if(*buf == '[') {
      sb_match(&buf,&tmpSpeech,cfg);
      continue;
    }

    if(*buf == '{') {
      if(! cb_match(&buf,&tmpSpeech,cfg)) {
      	tmpSpeech = *speech;

      	while(!(buf == *buffer || *buf == ',')) {
      	  ++buf;
      	}
      }
      continue;
    }
    
    if(*buf == '\\') { // We will check what is after it.
      ++buf;
    }

    if(*buf == *tmpSpeech) {
      ++buf;
      ++tmpSpeech;
    } else {
      tmpSpeech = *speech;

      while(!(buf == *buffer || *buf == ',')) {
      	++buf;
      }
    }
  } //end while
  
  if(tmpSpeech > Gspeech) {
    Gspeech = tmpSpeech;
    tmpSpeech = *speech;
  }
  ++buf;
  *buffer = buf;

  if(Gspeech > *speech) {
    *speech = Gspeech;
    return 1;
  }

  return 0;
}

// curly bracket match
// differently from any_match() this is not recursive
int cb_match(char **buffer,char **speech,struct config *cfg) {

  char start = '{';
  char end = '}';

  if(**buffer != start) {
    printf("ERROR, any_atomic_match() called, but **buffer != '%c'\n",
	   start);
  }
  ++(*buffer);

  char *buf = *buffer;

  int stop = 1;
  
  while (stop != 0) {
    if(**buffer == '\n' || **buffer == '\0' || **buffer == '\r' || **buffer == start) {
      printf("ERROR, inconnect syntax of %c,%c.\n",start,end);
      exit(1);
    }
    if(**buffer == end) {
      --stop;
    }
    ++(*buffer);
    if(**buffer == '\\') {
      // Not sure about the flows of these ifs
      ++(*buffer);
      if(**buffer != '\0')
	     ++(*buffer);
    }
  }
  
  --(*buffer);
  **buffer = '\0';
  //Now *buf is a file name
  
  struct config newcfg;
  newcfg.match_first = 1;
  newcfg.starting_db_line = 0;
  newcfg.current_db_line = 0;
  newcfg.end_of_match = 0;
  newcfg.var_Header = NULL;
  newcfg.var_LL = NULL;
  newcfg.database = malloc(sizeof(char)*strlen(buf)+1); strcpy(newcfg.database,buf);
  newcfg.speech = malloc(sizeof(char)*strlen(*speech)+1); strcpy(newcfg.speech,*speech);
  newcfg.command = NULL;
  
  get_command(&newcfg);
  
  printf("any_atomic_match: %s,%d.\n", newcfg.command, newcfg.end_of_match); //DEBUG
  
  //FIXME: here we must save newcfg.command somewhere
  
  int ret = (newcfg.command != NULL && *newcfg.command != '\0');
  
  if (ret) {
    *speech += newcfg.end_of_match;
    **buffer = '}';
    ++(*buffer);
    //Probably we should now duplicate speech....
  }
  
  free_structure(&newcfg);
  return ret;
}


/**
* Return the remaining part of the line
*/
char *line_match(char *buf,char **tmpSpeech,struct config *cfg) {
  // buf should be right before the name of the
  // variable, on a space. What we need to do is skip the name
  // of the variable, and get the data we need so we can
  // stop we we hit a match. Then move tmpSpeech to to before that
  // however we also need to make sure *speech is moved after that
  // so we need an if statement for that.
  if(*buf != ' ') {
    printf("Incorrect syntax in line_match!\n");
    exit(1);
  }


  while(*buf == ' ') {
    ++buf;
  }
  if(*buf == ')' || *buf == '\n' ||
     *buf == '\r' || *buf == '\0') {
    printf("Incorrect syntax in line_match!\n");
    exit(1);
  }

  // We are at the varName, lets pass it.
  while(*buf != ' ' && *buf != '\n' && *buf != '\r' &&
    *buf != '\0' && *buf != ')') {
    ++buf;
  }
  if(*buf == ')') { // This means it matches the rest of
		                // the speech

    *tmpSpeech = *tmpSpeech + strlen(*tmpSpeech);

    return *tmpSpeech;
  }
  if(*buf != ' ') {
    printf("Incorrect syntax in line_match!\n");
    exit(1);
  }
  while(*buf == ' ') {
    ++buf;
  }
  if(*buf == '\n' || *buf == '\0' || *buf == '\r') {
    printf("Incorrect syntax in line_match!\n");
    exit(1);
  }
  if(*buf == ')') {
    *tmpSpeech = *tmpSpeech + strlen(*tmpSpeech);
    return *tmpSpeech;
  }

  char *matchExpression;
  // Okay we are finally at the start of the end-expression.
  matchExpression = buf;
  // okay lets send buf to ) and make sure everything checks out.

  while(*buf != ')' && *buf != '\0') {
    if(*buf == '(') {
      printf("Not allowed, no variables in an end-expression!\n");
      exit(1);
    }
    ++buf;
  }
  if(*buf != ')') {
    printf("Incorrect syntax in line_match!\n");
    exit(1);
  }
  // Finally we are here, we can now start building out Line.

  //reusing buf, we know we have a ) to stop at.
  buf = matchExpression;
  char *speechChecker = *tmpSpeech;
  char *speechWalker  = *tmpSpeech;

  // Now for each character until you either get a match
  // or hit '\0' or '\n', check if there is a match with
  // match expression. When you do, set tmpSpeech to *before*
  // it and return a pointer to *after* it.
  // if '\0' or '\n' is hit, set tmpSpeech to it's orginal postion
  // and return NULL. (alternativly don't change it.


  // Allows optional stop to work
  int only_sb = 1;
  while(*speechWalker != '\0' && *speechWalker != '\n' && *speechWalker != '\r') {

    while(*buf != ')') {
      if(*buf == '<') {
	only_sb = 0;
	if(! lt_match(&buf,&speechChecker,cfg)) {
	  buf = matchExpression;
	  speechChecker = speechWalker;
	  break;
	}
	continue;
      } else if(*buf == '[') {
	sb_match(&buf,&speechChecker,cfg);
	continue;
      }
      if(*buf != *speechChecker) {
	only_sb = 0;
	break;
      }
      ++buf;
      ++speechChecker;
    }
    if(*buf != ')') { // no dice
      buf = matchExpression;
      speechChecker = speechWalker;
    } else { // we have a match
      if(speechChecker > speechWalker) { // If there is nothing to put in
				      // the variable, it's not a match.
	*tmpSpeech = speechWalker;
	return speechChecker;
      } else {
	buf = matchExpression;
	speechChecker = speechWalker;
      }
    }
    ++speechWalker;
    ++speechChecker;
  }
  if (only_sb) {
    *tmpSpeech = *tmpSpeech + strlen(*tmpSpeech);
    return *tmpSpeech;
  }

  return NULL;
}

/**
* Return true if the text contained in /speech/ (input) matches the text-pattern contained in /buf/ (line of dictionary)
* Assumes there are no blanks at the beginning
*/
int is_match(char *speech,char *buf,struct config *cfg) {
  char *ptr;
  char *speechPtr;

  ptr = buf;

  // Check if the line is empty
  if(*ptr == '\n' || *ptr == '\0' || *ptr == '\r')
    return 0;

  // Check if line is a comment.
  if(*ptr == '#')
    return 0;

  // Check if line is a command.
  if(*ptr == ' ' || *ptr == '\t')
    return 0;

  // If we get here, check if they are equal.
  speechPtr = speech;

  return check_equality(speechPtr,ptr,cfg);
}

int is_eow(char c) {
    return c == ' ' || c == ',' || c == ';' || c == '.' || c == ':' ;
}

int check_equality(char *speech,char *buffer,struct config *cfg) {
  // if there is a < in buffer, don't move the speech pointer,
  // try to match from that point everything in <a,b,c>
  // and then move the speech pointer to the end of the biggest match
  // if nothing matches, return a 0.
  //
  // If there is a [ hit in the buffer, don't move the speech pointer,
  // act exactly like <>,matching the largest possible.
  // however, this time if nothing matches, simply do not move the
  // speech pointer and go the the next thing in the buffer.
  //
  // If you hit a (,first check if it is a type<li,st> and just treat
  // it as <> (but convert to number if it is type Number.
  //
  // Otherwise, just read as much as the type needs. But don't save the
  // data here.
  //
  // \< \( and \[ are treated as their literal values.

  //  printf("Testing if %s == %s\n",speech,buffer); // DEBUG

  char* savespeech = speech;

  while(1) {
    //printf("DEBUG matching buf='%s' speech='%s'\n", buffer, speech); //DEBUG
    if(*buffer == '\n' || *buffer == '#' || *buffer == '\r') {
      *buffer = '\0';
    }
    //printf("Going to match: %c,%c.\n",*buffer,*speech);  //DEBUG
    if(*buffer == '\0') {
      if (*speech == '\0') //both buffer and speech ended
        break;
      else if (cfg->match_first && is_eow(*speech)) //speech not ended, however we just want first match
        break;
    } else if((*speech == '\0') && (*buffer != '[')) {//speech ended but buffer did not
      return 0;
    }

    if (*buffer == '<') {
      if(! lt_match(&buffer,&speech,cfg)) {
      	return 0;
      }
      // If there is a match here, both speech and buffer
      // will be in the right place.
      continue;
    }
    else if (*buffer == '[') {
      sb_match(&buffer,&speech,cfg);
      // Same as lt_match, but not need to return no match
      // if nothing is found, that is okay.
      continue;
    }
    else if(*buffer == '(') {
      if( ! op_match(&buffer,&speech,cfg)) {
        return 0;
      }

      continue;
    }
    else if(*buffer == '{') {
      if( ! cb_match(&buffer,&speech,cfg)) {
        return 0;
      }
      
      continue;
    }
    else if(*buffer == '\\') {
      ++buffer;
      // Duplicates ??
      if(*speech != *buffer)
        return 0;
      }
    else {
      if(*speech != *buffer) {
      	//printf("%c != %c\n",*speech,*buffer); // DEBUG
      	return 0;
      }
      ++buffer;
      ++speech;
    }
  }
  cfg->end_of_match = speech - savespeech;
  return 1;
}


