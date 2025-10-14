PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE individuals (
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
INSERT INTO individuals VALUES(1,'unknown',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'other',NULL,NULL,'prospect',replace('## Subject: Following up from our meeting\n\nHi [Name],\n\nThanks for taking the time to meet. I wanted to follow up on our conversation and confirm next steps.\n\n### Key Points\n- Point 1 from discussion\n- Point 2 from discussion\n\n### Next Steps\n- Action item 1\n- Action item 2\n\nLooking forward to staying in touch!\n\nBest,\nVrijen','\n',char(10)),NULL,'Careerspan/Meetings/2025-10-10_0023_sales_unknown_9366/stakeholder-profile.md','2025-10-10 04:54:47','2025-10-10 12:44:48',NULL);
CREATE TABLE interactions (
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
CREATE TABLE relationships (
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
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('individuals',1);
CREATE INDEX idx_individuals_company ON individuals(company);
CREATE INDEX idx_individuals_category ON individuals(primary_category);
CREATE INDEX idx_individuals_status ON individuals(status);
CREATE INDEX idx_individuals_last_interaction ON individuals(last_interaction_date);
CREATE INDEX idx_interactions_date ON interactions(interaction_date);
CREATE INDEX idx_interactions_individual ON interactions(individual_id);
CREATE VIEW active_prospects AS
SELECT 
    i.*,
    MAX(int.interaction_date) as last_contact
FROM individuals i
LEFT JOIN interactions int ON i.id = int.individual_id  
WHERE i.status = 'active' AND i.primary_category = 'prospect'
GROUP BY i.id
ORDER BY last_contact DESC;
CREATE VIEW stale_contacts AS
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
CREATE TRIGGER update_individuals_timestamp 
AFTER UPDATE ON individuals
BEGIN
    UPDATE individuals SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;
CREATE TRIGGER update_last_interaction_date
AFTER INSERT ON interactions
BEGIN
    UPDATE individuals 
    SET last_interaction_date = NEW.interaction_date
    WHERE id = NEW.individual_id
    AND (last_interaction_date IS NULL OR NEW.interaction_date > last_interaction_date);
END;
COMMIT;
