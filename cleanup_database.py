#!/usr/bin/env python3
"""
Database cleanup script to remove astrology-specific data and schema
This will transform the database from astrology schema to clean auth template
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from dotenv import load_dotenv

load_dotenv()

def cleanup_database():
    """Clean up astrology-specific tables and columns"""
    
    database_url = os.getenv("DATABASE_URL", "postgresql://astrosim_user:your_secure_password@localhost:5432/astrosim_db")
    engine = create_engine(database_url)
    
    print("🧹 Starting database cleanup...")
    print("=" * 50)
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                print("1. 📊 Checking current tables...")
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """))
                current_tables = [row[0] for row in result]
                print(f"   Found tables: {', '.join(current_tables)}")
                
                # Step 1: Drop astrology-specific tables
                print("\n2. 🗑️ Dropping astrology-specific tables...")
                astrology_tables = ['birth_charts', 'saved_locations', 'astro_calculations_cache']
                
                for table in astrology_tables:
                    if table in current_tables:
                        print(f"   Dropping {table}...")
                        conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    else:
                        print(f"   ⚠️ Table {table} not found (already removed?)")
                
                # Step 2: Check current users table structure
                print("\n3. 🔍 Checking users table structure...")
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND table_schema = 'public'
                    ORDER BY ordinal_position;
                """))
                user_columns = [(row[0], row[1], row[2]) for row in result]
                print("   Current users table columns:")
                for col, dtype, nullable in user_columns:
                    print(f"     - {col} ({dtype}, {'NULL' if nullable == 'YES' else 'NOT NULL'})")
                
                # Step 3: Remove astrology-specific columns from users table
                print("\n4. ✂️ Removing astrology columns from users table...")
                astrology_columns = ['birth_date', 'birth_time', 'birth_city', 'birth_latitude', 'birth_longitude']
                
                for column in astrology_columns:
                    if any(col[0] == column for col in user_columns):
                        print(f"   Dropping column {column}...")
                        conn.execute(text(f"ALTER TABLE users DROP COLUMN IF EXISTS {column}"))
                    else:
                        print(f"   ⚠️ Column {column} not found (already removed?)")
                
                # Step 4: Add auth template columns
                print("\n5. ➕ Adding auth template columns...")
                new_columns = [
                    ("phone", "VARCHAR(50)"),
                    ("address", "TEXT"),
                    ("city", "VARCHAR(255)"),
                    ("country", "VARCHAR(255)")
                ]
                
                for col_name, col_type in new_columns:
                    if not any(col[0] == col_name for col in user_columns):
                        print(f"   Adding column {col_name}...")
                        conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                    else:
                        print(f"   ✅ Column {col_name} already exists")
                
                # Step 5: Update user_preferences table if needed
                print("\n6. 🔧 Updating user_preferences table...")
                
                # Check if user_preferences has astrology-specific columns
                result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns 
                    WHERE table_name = 'user_preferences' AND table_schema = 'public'
                    ORDER BY ordinal_position;
                """))
                pref_columns = [row[0] for row in result]
                
                astro_pref_columns = ['default_house_system', 'chart_style_preferences']
                for column in astro_pref_columns:
                    if column in pref_columns:
                        print(f"   Dropping column {column} from user_preferences...")
                        conn.execute(text(f"ALTER TABLE user_preferences DROP COLUMN IF EXISTS {column}"))
                
                # Ensure auth template columns exist in user_preferences
                auth_pref_columns = [
                    ("theme", "VARCHAR(50) DEFAULT 'light'"),
                    ("language", "VARCHAR(10) DEFAULT 'en'"),
                    ("notifications_enabled", "BOOLEAN DEFAULT true")
                ]
                
                for col_name, col_def in auth_pref_columns:
                    if col_name not in pref_columns:
                        print(f"   Adding column {col_name} to user_preferences...")
                        conn.execute(text(f"ALTER TABLE user_preferences ADD COLUMN {col_name} {col_def}"))
                    else:
                        print(f"   ✅ Column {col_name} already exists in user_preferences")
                
                # Commit transaction
                trans.commit()
                print("\n✅ Database cleanup completed successfully!")
                
            except Exception as e:
                trans.rollback()
                raise e
                
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        return False
    
    return True

def verify_cleanup():
    """Verify the cleanup was successful"""
    print("\n7. ✅ Verifying cleanup...")
    
    database_url = os.getenv("DATABASE_URL", "postgresql://astrosim_user:your_secure_password@localhost:5432/astrosim_db")
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Check remaining tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            
            print("   📋 Remaining tables:")
            expected_tables = ['users', 'user_preferences', 'user_sessions']
            for table in tables:
                status = "✅" if table in expected_tables else "⚠️"
                print(f"     {status} {table}")
            
            # Check users table structure
            result = conn.execute(text("""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = 'users' AND table_schema = 'public'
                ORDER BY ordinal_position;
            """))
            user_cols = [row[0] for row in result]
            
            print("   👤 Users table columns:")
            expected_user_cols = ['id', 'keycloak_id', 'full_name', 'phone', 'address', 'city', 'country', 'timezone', 'created_at', 'updated_at']
            for col in user_cols:
                status = "✅" if col in expected_user_cols else "⚠️"
                print(f"     {status} {col}")
            
            # Check for any remaining astrology columns
            astro_cols = ['birth_date', 'birth_time', 'birth_city', 'birth_latitude', 'birth_longitude']
            remaining_astro = [col for col in user_cols if col in astro_cols]
            if remaining_astro:
                print(f"   ❌ Still have astrology columns: {remaining_astro}")
                return False
            else:
                print("   ✅ No astrology columns remaining")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False

def backup_data():
    """Create a backup before cleanup"""
    print("0. 💾 Creating backup (optional)...")
    print("   Run this manually if you want a backup:")
    print("   sudo -u postgres pg_dump astrosim_db > astrosim_db_backup_$(date +%Y%m%d_%H%M%S).sql")
    
    response = input("\n   Continue without backup? (y/N): ").lower()
    if response != 'y':
        print("   Backup recommended. Exiting...")
        return False
    return True

def main():
    print("🧹 Database Cleanup for Auth Template")
    print("=" * 50)
    print("This will remove all astrology-specific tables and columns")
    print("and transform your database to match the cleaned auth template.")
    print("\n⚠️  WARNING: This will permanently delete astrology data!")
    
    # Check if user wants to continue
    response = input("\nContinue? (y/N): ").lower()
    if response != 'y':
        print("Cleanup cancelled.")
        return
    
    # Optional backup
    if not backup_data():
        return
    
    # Perform cleanup
    if cleanup_database():
        if verify_cleanup():
            print("\n🎉 Database successfully cleaned!")
            print("\nYour database now matches the auth template schema.")
            print("You can now run your cleaned application.")
        else:
            print("\n⚠️ Cleanup completed but verification found issues.")
    else:
        print("\n❌ Cleanup failed!")

if __name__ == "__main__":
    main()
