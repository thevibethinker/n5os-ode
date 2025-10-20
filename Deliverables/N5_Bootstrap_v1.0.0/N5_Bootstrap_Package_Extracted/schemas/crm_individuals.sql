-- CRM Individuals Database Schema
-- Tracks people in your network with rich metadata and relationships

-- Core individual/contact information
CREATE TABLE IF NOT EXISTS individuals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Basic Info
    full_name TEXT NOT NULL,
    preferred_name TEXT,
    title TEXT,
    company TEXT,  -- Simple text for now, can FK to orgs table later
    
    -- Contact Details
    email TEXT,
    phone TEXT,
    linkedin_url TEXT,
    twitter_handle TEXT,
    
    -- Classification
    primary_category TEXT CHECK(primary_category IN (
        'prospect',      -- Potential customer/partner
        'customer',      -- Active customer
        'channel_partner', -- Distribution/partnership
        'investor',      -- Funding source
        'advisor',       -- Provides guidance
        'referral_source', -- Introduces others
        'community',     -- Network/ecosystem
        'other'
    )),
    
    -- Relationship metadata
    source_type TEXT,  -- How you met (conference, referral, cold, etc.)
    referrer_id INTEGER,  -- FK to individuals(id) if referred
    status TEXT CHECK(status IN (
        'active',
        'prospect', 
        'dormant',
        'archived'
    )) DEFAULT 'prospect',
    
    -- Context
    notes TEXT,  -- Brief notes (longer content stays in markdown)
    tags TEXT,  -- Comma-separated tags for flexible categorization
    
    -- Links to markdown files
    markdown_file_path TEXT,  -- Relative path like 'Knowledge/crm/individuals/jane-smith.md'
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction_date DATE,
    
    -- Constraints
    FOREIGN KEY (referrer_id) REFERENCES individuals(id)
);

-- Interaction history (meetings, emails, calls)
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    individual_id INTEGER NOT NULL,
    
    interaction_type TEXT CHECK(interaction_type IN (
        'meeting',
        'email', 
        'call',
        'linkedin',
        'event',
        'other'
    )),
    
    interaction_date DATE NOT NULL,
    subject TEXT,
    summary TEXT,
    
    -- Optional links to artifacts
    notes_file_path TEXT,  -- Link to meeting notes markdown
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (individual_id) REFERENCES individuals(id) ON DELETE CASCADE
);

-- Person-to-person relationships (mutual connections, referrals)
CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_a_id INTEGER NOT NULL,
    person_b_id INTEGER NOT NULL,
    
    relationship_type TEXT CHECK(relationship_type IN (
        'mutual_acquaintance',
        'referral',  -- person_a referred person_b
        'colleague',
        'partner',
        'other'
    )),
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (person_a_id) REFERENCES individuals(id) ON DELETE CASCADE,
    FOREIGN KEY (person_b_id) REFERENCES individuals(id) ON DELETE CASCADE,
    
    -- Prevent duplicate relationships
    UNIQUE(person_a_id, person_b_id, relationship_type)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_individuals_company ON individuals(company);
CREATE INDEX IF NOT EXISTS idx_individuals_category ON individuals(primary_category);
CREATE INDEX IF NOT EXISTS idx_individuals_status ON individuals(status);
CREATE INDEX IF NOT EXISTS idx_individuals_last_interaction ON individuals(last_interaction_date);
CREATE INDEX IF NOT EXISTS idx_interactions_date ON interactions(interaction_date);
CREATE INDEX IF NOT EXISTS idx_interactions_individual ON interactions(individual_id);

-- Useful views for common queries
CREATE VIEW IF NOT EXISTS active_prospects AS
SELECT 
    i.*,
    MAX(int.interaction_date) as last_contact
FROM individuals i
LEFT JOIN interactions int ON i.id = int.individual_id  
WHERE i.status = 'active' AND i.primary_category = 'prospect'
GROUP BY i.id
ORDER BY last_contact DESC;

CREATE VIEW IF NOT EXISTS stale_contacts AS
SELECT 
    i.*,
    MAX(int.interaction_date) as last_contact,
    julianday('now') - julianday(MAX(int.interaction_date)) as days_since_contact
FROM individuals i
LEFT JOIN interactions int ON i.id = int.individual_id
WHERE i.status = 'active'
GROUP BY i.id
HAVING days_since_contact > 90 OR days_since_contact IS NULL
ORDER BY days_since_contact DESC;

-- Trigger to auto-update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_individuals_timestamp 
AFTER UPDATE ON individuals
BEGIN
    UPDATE individuals SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Trigger to update last_interaction_date when interaction added
CREATE TRIGGER IF NOT EXISTS update_last_interaction_date
AFTER INSERT ON interactions
BEGIN
    UPDATE individuals 
    SET last_interaction_date = NEW.interaction_date
    WHERE id = NEW.individual_id
    AND (last_interaction_date IS NULL OR NEW.interaction_date > last_interaction_date);
END;
