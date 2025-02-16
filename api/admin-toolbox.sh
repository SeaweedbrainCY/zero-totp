#! /bin/sh



# Check if the user has provided a command
if [ -z "$1" ]; then
    echo "###############################################"
    echo "# Zero-TOTP Toolbox Script                    #"
    echo "# A tool for administrators to interact with  #"
    echo "# the Zero-TOTP server management             #"
    echo "# Developed by Nathan Stchepinsky             #"
    echo "###############################################"
    echo ""
    echo "Available Commands:"
    echo "  - rotate-sse-key    : Rotate the SSE (Server-Side Encryption) key"
    echo "  - decrypt-db-entry  : Decrypt a specific entry in the Zero-TOTP database"
    echo "  - help  : to get help. You can also use help <command> to get help about a specific command"
    echo ""
    echo "Welcome to the Zero-TOTP Toolbox! Use the available commands to manage your server."
    echo ""
    echo "Please provide a command. Use 'help' to see the available commands."
    exit 1
fi

# Check if the user has provided a valid command
if [ "$1" != "rotate-sse-key" ] && [ "$1" != "decrypt-db-entry" ] && [ "$1" != "help" ]; then
    echo "Invalid command. Use 'help' to see the available commands."
    exit 1
fi

# Handle the 'help' command
if [ "$1" = "help" ]; then
    
    if [ -z "$2" ]; then
        echo "Welcome to the Zero-TOTP Toolbox! Use the available commands to manage your server."
        echo ""
        echo "Available Commands:"
        echo "  - rotate-sse-key    : Rotate the SSE (Server-Side Encryption) key"
        echo "  - decrypt-db-entry  : Decrypt a specific entry in the Zero-TOTP database" 
        echo "" 
        echo "Use 'help <command>' to get help about a specific command."
        exit 0
    elif [ "$2" = "decrypt-db-entry" ]; then
        echo "decrypt-db-entry command:"
        echo "  - Usage: decrypt-db-entry <table-name> <entry-id>"
        echo "  - Description: Decrypt a specific entry in the Zero-TOTP database. You'll need to provide the table name and entry ID."
        echo "  - Arguments:"
        echo "      - table-name: The name of the table you want to decrypt an entry from."
        echo "      - entry-id: The ID of the entry you want to decrypt."
        echo "  - Example: decrypt-db-entry oauth_tokens 10"
        echo ""
        echo "Supported tables:"
        echo "  - oauth_tokens"
        echo ""
        exit 0
    elif [ "$2" = "rotate-sse-key" ]; then
        echo "rotate-sse-key command:"
        echo "  - Usage: rotate-sse-key"
        echo "  - Description: Rotate the SSE (Server-Side Encryption) key. This will generate a new key and re-encrypt all the data in the database."
        echo "  - Example: rotate-sse-key"
        exit 0
    else
        echo "Invalid command. Use 'help' to see the available commands."
        exit 1
    fi

elif [ "$1" = "rotate-sse-key" ]; then
    echo "###### Script init loading ... ######"
    echo ""
    export PYTHONPATH=$(pwd)
    venv/bin/python ./toolbox_scripts/update_server_side_encryption_key.py
    exit 0

elif [ "$1" = "decrypt-db-entry" ]; then
    if [ -z "$2" ] || [ -z "$3" ]; then
        echo "Invalid arguments. Usage: decrypt-db-entry <table-name> <entry-id>"
        echo ""
        echo "Use 'help decrypt-db-entry' to get more information."
        exit 1
    fi
    echo "###### Script init loading ... ######"
    echo ""
    export PYTHONPATH=$(pwd)
    venv/bin/python ./toolbox_scripts/decrypt_database_entry.py $2 $3
    exit 0
 
else 
    echo "Invalid command. Use 'help' to see the available commands."
    exit 1
fi

