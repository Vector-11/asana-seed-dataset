#!/usr/bin/env python3
"""
Database Viewer for Asana Simulation Database
Displays tables in formatted view with all columns visible
"""

import sqlite3
from pathlib import Path
import sys
from typing import List, Tuple

class DatabaseViewer:
    """View and explore the Asana simulation database"""
    
    def __init__(self, db_path: str = "output/asana_simulation.sqlite"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            print(f"❌ Database not found at {self.db_path}")
            print("Run 'python src/main.py' first to generate the database")
            sys.exit(1)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def list_all_tables(self):
        """List all tables with record counts"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row[0] for row in self.cursor.fetchall()]
        
        print("\n" + "="*100)
        print("📋 ALL TABLES IN DATABASE")
        print("="*100)
        print(f"{'#':<3} {'Table Name':<30} {'Record Count':<15} {'Description'}")
        print("-"*100)
        
        total_records = 0
        descriptions = {
            'organizations': 'Top-level workspace',
            'teams': 'Groups within organization',
            'users': 'Organization members with profiles',
            'team_members': 'Team membership mappings',
            'projects': 'Collections of tasks',
            'project_members': 'Project membership',
            'sections': 'Status columns within projects',
            'tags': 'Labels for categorizing',
            'tasks': 'Work items (CORE)',
            'task_tags': 'Task categorization',
            'comments': 'Discussion on tasks'
        }
        
        for i, table in enumerate(tables, 1):
            self.cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = self.cursor.fetchone()[0]
            total_records += count
            desc = descriptions.get(table, '')
            print(f"{i:<3} {table:<30} {count:>15,} {desc}")
        
        print("-"*100)
        print(f"{'TOTAL':<3} {'':<30} {total_records:>15,}")
        print("="*100 + "\n")
    
    def display_table(self, table_name: str, limit: int = 10):
        """Display table data in formatted view"""
        
        # Validate table exists
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        if not self.cursor.fetchone():
            print(f"❌ Table '{table_name}' not found")
            return
        
        # Get total count
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        total_count = self.cursor.fetchone()[0]
        
        # Get data
        self.cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
        rows = self.cursor.fetchall()
        
        if not rows:
            print(f"❌ Table '{table_name}' is empty")
            return
        
        # Get column information
        columns = [description[0] for description in self.cursor.description]
        
        print("\n" + "="*150)
        print(f"📊 TABLE: {table_name.upper()}")
        print(f"   Total Records: {total_count:,} | Showing: {len(rows)}")
        print("="*150)
        
        # Calculate column widths
        col_widths = {}
        for col in columns:
            col_widths[col] = max(len(col), 12)
        
        for row in rows:
            for col, val in zip(columns, row):
                val_str = str(val) if val is not None else "NULL"
                col_widths[col] = max(col_widths[col], min(len(val_str), 40))
        
        # Print column headers
        header = ""
        for col in columns:
            header += f"{col:<{col_widths[col]}} | "
        print(header)
        
        # Print separator
        separator = ""
        for col in columns:
            separator += "-" * col_widths[col] + "-+-"
        print(separator)
        
        # Print rows with row numbers
        for row_num, row in enumerate(rows, 1):
            row_str = f"{row_num:<3} "
            for col, val in zip(columns, row):
                val_str = str(val) if val is not None else "NULL"
                if len(val_str) > 40:
                    val_str = val_str[:37] + "..."
                row_str += f"{val_str:<{col_widths[col]}} | "
            print(row_str)
        
        print("="*150 + "\n")
    
    def display_schema(self):
        """Display database schema"""
        self.cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name;")
        schemas = self.cursor.fetchall()
        
        print("\n" + "="*150)
        print("🗄️  DATABASE SCHEMA (DDL)")
        print("="*150)
        
        for schema in schemas:
            print(schema[0])
            print("\n")
        
        print("="*150 + "\n")
    
    def get_column_info(self, table_name: str):
        """Get detailed column information"""
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        columns = self.cursor.fetchall()
        
        return columns
    
    def display_column_details(self, table_name: str):
        """Display detailed column information"""
        columns = self.get_column_info(table_name)
        
        if not columns:
            print(f"❌ Table '{table_name}' not found")
            return
        
        print("\n" + "="*150)
        print(f"📋 COLUMN DETAILS FOR TABLE: {table_name.upper()}")
        print("="*150)
        print(f"{'#':<3} {'Column Name':<30} {'Data Type':<15} {'Not Null':<10} {'Primary Key':<12} {'Default':<20}")
        print("-"*150)
        
        for i, col in enumerate(columns, 1):
            cid, name, dtype, notnull, dflt_value, pk = col
            print(f"{i:<3} {name:<30} {dtype:<15} {'YES' if notnull else 'NO':<10} {'YES' if pk else 'NO':<12} {str(dflt_value) if dflt_value else '':<20}")
        
        print("="*150 + "\n")
    
    def export_to_csv(self, table_name: str, output_file: str = None):
        """Export table to CSV"""
        if output_file is None:
            output_file = f"{table_name}_export.csv"
        
        self.cursor.execute(f"SELECT * FROM {table_name};")
        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write headers
            f.write(",".join(columns) + "\n")
            
            # Write data
            for row in rows:
                values = []
                for val in row:
                    if val is None:
                        values.append("")
                    elif isinstance(val, str) and (',' in val or '"' in val):
                        values.append(f'"{val.replace(chr(34), chr(34)+chr(34))}"')
                    else:
                        values.append(str(val))
                f.write(",".join(values) + "\n")
        
        print(f"✅ Exported {table_name} to {output_file}")
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Main entry point"""
    
    viewer = DatabaseViewer()
    
    if len(sys.argv) < 2:
        print("\n" + "="*150)
        print("🗄️  ASANA SIMULATION DATABASE VIEWER")
        print("="*150)
        print("\nUsage:")
        print("  python view_db.py --list              # List all tables")
        print("  python view_db.py <table_name>        # View table (default 10 rows)")
        print("  python view_db.py <table_name> 20     # View table with 20 rows")
        print("  python view_db.py <table_name> --schema  # View table schema")
        print("  python view_db.py <table_name> --csv  # Export to CSV")
        print("\nExamples:")
        print("  python view_db.py users")
        print("  python view_db.py projects 15")
        print("  python view_db.py tasks --schema")
        print("  python view_db.py comments --csv")
        print("="*150 + "\n")
        
        viewer.list_all_tables()
        viewer.close()
        return
    
    command = sys.argv[1]
    
    if command == "--list":
        viewer.list_all_tables()
    
    elif command == "--schema":
        viewer.display_schema()
    
    else:
        table_name = command
        
        if len(sys.argv) > 2:
            if sys.argv[2] == "--schema":
                viewer.display_column_details(table_name)
            elif sys.argv[2] == "--csv":
                viewer.export_to_csv(table_name)
            else:
                try:
                    limit = int(sys.argv[2])
                    viewer.display_table(table_name, limit)
                except ValueError:
                    print(f"❌ Invalid argument: {sys.argv[2]}")
        else:
            viewer.display_table(table_name, 10)
    
    viewer.close()

if __name__ == "__main__":
    main()
