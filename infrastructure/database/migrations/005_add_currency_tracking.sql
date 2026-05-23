-- Migration 005: Add currency tracking to entities
-- Adds currency_code column to printers, filaments, and quotes tables
-- to track which currency was used when creating/updating each record

-- Add currency_code to printers table
ALTER TABLE printers ADD COLUMN currency_code TEXT DEFAULT 'PYG';

-- Add currency_code to filaments table  
ALTER TABLE filaments ADD COLUMN currency_code TEXT DEFAULT 'PYG';

-- Add currency_code to quotes table
ALTER TABLE quotes ADD COLUMN currency_code TEXT DEFAULT 'PYG';

-- Add foreign key constraints (SQLite supports FK but doesn't enforce ALTER TABLE FK)
-- These are informational for documentation purposes

-- Update existing records to use default currency (PYG)
UPDATE printers SET currency_code = 'PYG' WHERE currency_code IS NULL;
UPDATE filaments SET currency_code = 'PYG' WHERE currency_code IS NULL;
UPDATE quotes SET currency_code = 'PYG' WHERE currency_code IS NULL;

-- Create indexes for faster currency-based queries
CREATE INDEX IF NOT EXISTS idx_printers_currency ON printers(currency_code);
CREATE INDEX IF NOT EXISTS idx_filaments_currency ON filaments(currency_code);
CREATE INDEX IF NOT EXISTS idx_quotes_currency ON quotes(currency_code);
