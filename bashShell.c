#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string.h>
#include <ctype.h>
#include <sys/types.h>
#include <sys/wait.h>

void deleteSingle(char * single_ptr) 
{
    free(single_ptr);
}

void deleteDouble(char ** double_ptr)
{
    int i = 0; 
    while(*(double_ptr + i))
    {
        free(*(double_ptr + i));
        i++;
    }
    free(double_ptr);
}

void splitString(char * temp_arr, char ** arguments, char * delim, int * amp)
{
    char* token; 
    int count = 0;
    token = strtok(temp_arr, delim);

    while(token != NULL)
    {
        token = strcat(token, "\0");
        if(strcmp(token, "&") == 0)
        {
            *amp = 1;
        }
        else 
        {
            *(arguments + count) = calloc(strlen(token) + 1, sizeof(char));
            strcpy(*(arguments + count), token);
            // *(arguments + count) = token;
        }
        count++;
        token = strtok(NULL, delim);
    }
}

void createFilePath(char ** all_files, char * init_file, char * found_file, char * com)
{
    int count = 0;
    struct stat temp;
    while(*(all_files + count) != NULL)
    {
        strcpy(init_file, *(all_files + count)); 
        init_file = strcat(strcat(init_file, "/"), com); 
        if(lstat(init_file, &temp) == 0)
        {
            strcpy(found_file, init_file);
            break;
        }
        count++;
    }
    return;
}

void changeDirectory(char ** arguments)
{
    if(*(arguments + 1) != NULL)
    {
        chdir(*(arguments + 1));
    }
    else 
    {
        chdir(getenv("HOME"));
    }
    return; 
}

void checkBackgroundProcess(pid_t * all_process)
{
    int count = 0;
    int status;
    while(*(all_process + count))
    {
        if(waitpid(-1, &status, WNOHANG) > 0)
        {
            printf("<background process terminated with exit status 0>\n");
            *(all_process + count) = *(all_process + count + 1);
            
        }
        count++;
    }
}

int main() 
{
    int max_size = 1024;
    char * path = calloc(1024, sizeof(char));
    char ** files = calloc(512, sizeof(char));
    pid_t * process = calloc(1024, sizeof(pid_t));
    int process_count = 0;
    int * ampersand = calloc(1, sizeof(int));

    setvbuf( stdout, NULL, _IONBF, 0 );
    if(getenv("MYPATH") == NULL)
    {
        strcpy(path, "/bin:.");
    }
    else 
    {
        strcpy(path, getenv("MYPATH"));
    }

    splitString(path, files, ":", ampersand);
    while(1)
    {
        *ampersand = 0;
        if(process_count > 0)
        {
            checkBackgroundProcess(process);
        }

        printf("$ ");
        char * buffer = calloc(1024, sizeof(char));
        fgets(buffer, max_size, stdin); 

        if(strlen(buffer) <= 1)
        {
            deleteSingle(buffer);
            continue;
        }

        *(buffer + strcspn(buffer, "\n")) = 0;

        if(strcmp("exit", buffer) == 0)
        {
            printf("bye\n");
            deleteSingle(buffer);
            break;
        }

        //split string
        char** argv = calloc(1024, sizeof(char));
        splitString(buffer, argv, " ", ampersand);

        char* command = *(argv);
        if(strcmp(command, "cd") == 0)
        {
            changeDirectory(argv);
            deleteDouble(argv);
            deleteSingle(buffer);
            continue;
        }

        char* filepath = calloc(1024, sizeof(char)); 
        char* correct_filepath = calloc(1024, sizeof(char)); 

        createFilePath(files, filepath, correct_filepath, command);

        if(strlen(correct_filepath) > 0)
        {
            if(*(ampersand) == 1)
            {
                pid_t p = fork();
                *(process + process_count) = p; 
                process_count++;
                if(p == -1)
                {
                    perror("fork() failed");
                    deleteSingle(buffer);
                    deleteSingle(filepath);
                    deleteSingle(correct_filepath);
                    deleteDouble(argv);
                    break;
                }

                if(p == 0)
                {
                    //child process
                    
                    execv(correct_filepath, argv);

                    perror("<background process terminated abnormally>\n");
                    abort(); 
                }
                else 
                {
                    printf("<running background process \"%s\">\n", command);
                }
            }
            else 
            {
                pid_t p = fork();
                if(p == -1)
                {
                    perror("fork() failed");
                    deleteSingle(buffer);
                    deleteSingle(filepath);
                    deleteSingle(correct_filepath);
                    deleteDouble(argv);
                    break;
                }

                if(p == 0)
                {
                    //child process
                    execv(correct_filepath, argv);

                    perror("ERROR: child process terminated abnormally.");
                    abort(); 
                }
                else 
                {
                    //parent process 
                    int status; 
                    waitpid(p, &status, 0); 

                }
            }
            
        }
        else 
        {
            fprintf(stderr, "%s: command not found\n", command);
        }
        
        deleteSingle(buffer);
        deleteSingle(filepath);
        deleteSingle(correct_filepath);
        deleteDouble(argv);
    }
    deleteSingle(path);
    deleteDouble(files);
    free(process);
    free(ampersand);
    return EXIT_SUCCESS;
}