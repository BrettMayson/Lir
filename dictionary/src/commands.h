/*
 * commands.h
 *
 *  Created on: Mar 20, 2013
 *      Author: James Mcclain, Antonis Kalou
 */

#ifndef COMMANDS_H_
#define COMMANDS_H_

#include "globals.h"

char *get_command(struct config *cfg);
char *create_command(char *buf,struct config *cfg);

#endif /* COMMANDS_H_ */
