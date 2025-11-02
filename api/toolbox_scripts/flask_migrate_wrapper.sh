#!/bin/sh
cd ..
FLASK_EXECUTABLE="./venv/bin/flask --app app:flask"

run_flask_command() {
    echo "running $FLASK_EXECUTABLE "$@" 2>&1"
    command_output=$($FLASK_EXECUTABLE "$@" 2>&1)
    
    echo "$command_output"
    
    if echo "$command_output" | grep -qiE 'drop|removed'; then
        echo 
        echo "THIS IS A WARNING"
        echo "THE MIGRATION PROCESS MAY HAVE INSTRCUTED THE DROP OF ONE OR MULTIPLE TABLES"
        echo "REVIEW THE VERSION FILE AND DO NOT PUSH UNWANTED CHANGES"
        echo 
        echo "Enter anything to acknowledge"
        echo 
        read _
    fi
}

. venv/bin/activate
case $1 in
    "db")
        case $2 in
            "init" | "migrate" | "upgrade" | "downgrade")
                run_flask_command "$@"
                ;;
            *)
                echo "Commande non prise en charge : $2"
                ;;
        esac
        ;;
    *)
        echo "Usage: $0 db [init|migrate|upgrade|downgrade]"
        ;;
esac

