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



// The first line returned is the command to execute.
// The 2nd line to return is the line number the match was at
// if requested. This is so in a dictionary with mutiple matchs
// for one sentence, they can all be found by running the program again
// with that line+1.
//
// If you don't want to skip any terms but want a number back, just tell
// it to start at 0.
//
// If there is no match, the program will return "No Command recognized.
// *and* exit with the exit code 2. 
// All other errors have the exit code one.

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "match.h"
#include "commands.h"



/***********************************************************************
  PROTOTYPES
************************************************************************/

static int parse_args(int argc,char *argv[],struct config *cfg);

// Print with everything after the first space in single quotes
// to stop the shell from getting to it.

// ie. testing 1 2 3
// becomes
// testing '1 2 3'
static void print_arg_quoted(char *string);

void free_structure(struct config *cfg);


void str_lower(char *str) {
  char* pstr = str;
  while (*pstr++)
    *pstr = (char)tolower(*pstr);
}

int main(int argc, char *argv[]) {
   
  struct config cfg;
  cfg.match_first = 0; //option (boolean): match first line only
  cfg.starting_db_line = 0;    //option: starting line
  cfg.current_db_line = 0;
  cfg.end_of_match = 0;  //in most cases this will be strlen(speech)
  cfg.var_Header = NULL;
  cfg.var_LL = NULL;
  cfg.speech = NULL; // What the user said.
  cfg.database = NULL; // File to check what command to run
			 // based on what was said.
  cfg.command = NULL; // The command to run.
  
  
  if(parse_args(argc,argv,&cfg) != 0) {
    exit(EXIT_FAILURE);
  }
  str_lower(cfg.speech);  
  get_command(&cfg);

  if(cfg.command) {
    printf("%s\n",cfg.command);
    if(cfg.starting_db_line > 0) { // if we ask for a line, we get one back.
      printf("%d\n",cfg.current_db_line-1);
    }
  }else{
    return 1;
  }
    
  free_structure(&cfg);

  return 0;
}

// Free elements in struct, not struct itself
// No oppression allowed in this program.
void free_structure(struct config *cfg) {
  free(cfg->speech);
  if (cfg->command) free(cfg->command);
  while(cfg->var_Header) {
      free(cfg->var_Header->varName);
      free(cfg->var_Header->varValue);
      cfg->var_LL = cfg->var_Header->next;
      free(cfg->var_Header);
      cfg->var_Header = cfg->var_LL;
  }
  free(cfg->database);
}

static void print_arg_quoted(char *string) {
  while(*string != ' ' && *string != '\0') {
    printf("%c",*string);
    ++string;
  }
  if(*string != '\0') {
    printf("%c",*string);
  } else {
    printf("\n");
    return;
  }
  ++string;
  printf("'");
  while(*string != '\0') {
    if(*string == '\'') {
      printf("'\"'\"'");
    }
    else {
      printf("%c",*string);
    }
    ++string;
  }
  printf("'");
  printf("\n");
  
  return;
}

static int parse_args(int argc,char *argv[],struct config *cfg) {

  if(argc < 3 || (argc >= 1 && strcmp(argv[1], "-h") == 0)) {
    printf("Incorrect number of arguments: \n"
	   "USAGE %s <speech> <database> [-f ][-s starting-line]\n",argv[0]);
    return 1;
  }
  if(cfg->speech != NULL || cfg->database != NULL) {
    fprintf(stderr,"ERROR, speech and database pointers must be NULL\n"
	    "before calling parse_args().");
    return 1;
  }
  cfg->speech = malloc(sizeof(char)*strlen(argv[1])+1);
  cfg->database = malloc(sizeof(char)*strlen(argv[2])+1);

  if(cfg->speech == NULL || cfg->database == NULL) {
   perror("malloc:");
   exit(EXIT_FAILURE);
  }
  strcpy(cfg->speech,argv[1]);
  strcpy(cfg->database,argv[2]);
  
  //more options
  int curarg = 2;
  cfg->match_first = 0;
  cfg->starting_db_line = 0;
  while ( ++curarg < argc ) {
  
    if (strcmp(argv[curarg], "-f") == 0) {
      cfg->match_first = 1;
      
    } else if(strcmp(argv[curarg], "-s") == 0) {
      if (++curarg >= argc) {
        fprintf(stderr,"ERROR, option -s expects a line number.\n");
        return 1;
      }
      int i = -1;
      sscanf(argv[curarg],"%d",&i);
      if(i <= 0) {
        fprintf(stderr,"'%s' is not a valid line to start on.\n",argv[curarg]);
        return 1;
      }
      cfg->starting_db_line = i-1;
      
    } else {
      fprintf(stderr,"ERROR, unknown option: %s.\n", argv[curarg]);
      return 1;
    }
  }
  
  return 0;
}


