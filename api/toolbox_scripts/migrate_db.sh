#! /bin/sh

echo ""
echo "##### CRITICAL OPERATION #####"
echo "Please BACKUP your database before proceeding."
echo "Follow this doc to backup your database: https://docs.zero-totp.com/latest/self-host/admin/database-backup/"
echo ""
echo -e "Did you backup your database? (yes/NO) \c"
read backup_confirmation
if [ "$backup_confirmation" != "yes" ]; then
    echo "Please backup your database before proceeding."
    exit 0
fi
echo ""
echo "Starting the database migration process..."
echo ""
echo "Migrating the database..."
echo "" 
alembic upgrade head > /tmp/alembic_upgrade.log 2>&1
if [ $? -eq 0 ]; then 
    echo ""
    echo "🎉  Database migration completed successfully."
    echo ""

else
    echo "##### Error trace #####"
    cat /tmp/alembic_upgrade.log
    echo "##### Error trace #####"
    echo ""
    echo "❌  An error occurred while migrating the database. Check the error message above to understand what happened."
    echo ""
fi