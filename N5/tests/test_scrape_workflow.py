import unittest
from unittest.mock import patch, MagicMock
from N5.jobs.workflows.scrape_workflow import ScrapeWorkflow

class TestScrapeWorkflow(unittest.TestCase):
    def setUp(self):
        self.workflow = ScrapeWorkflow()

    @patch('N5.jobs.modules.ats_detector.detect_ats')
    @patch('N5.jobs.modules.ats_scraper.scrape_jobs')
    @patch('N5.jobs.modules.fallback_scraper.FallbackScraper.scrape_jobs')
    @patch('N5.jobs.modules.dedup.deduplicate')
    @patch('N5.jobs.modules.bs_filter.filter_job')
    @patch('N5.jobs.modules.description_enricher.enrich_description')
    @patch('N5.jobs.modules.list_writer.append_job')
    def test_execute_scraping(self, mock_append, mock_enrich, mock_filter, mock_dedup, mock_fallback_scrape, mock_scrape, mock_detect):
        # Arrange
        mock_detect.side_effect = [None, {'careers_url': 'https://mockcompany.com/careers', 'ats': 'greenhouse'}]
        mock_fallback_scrape.return_value = [{'url': 'https://mockcompany.com/job1', 'title': 'Product Manager', 'company': 'MockCompany', 'location': 'NY'}]
        mock_scrape.return_value = [{'url': 'https://mockcompany.com/job2', 'title': 'Product Owner', 'company': 'MockCompany', 'location': 'NY'}]
        mock_dedup.side_effect = lambda new, old: new
        mock_filter.side_effect = lambda job: {'verdict': 'pass', 'score': 1.0, 'flags': []}
        mock_enrich.side_effect = lambda url: 'Full job description text'

        companies = ['NoATSSupport', 'MockCompany']
        roles = ['Product Manager']

        # Act
        result = self.workflow.execute_scraping(companies, roles, 'jobs-scraped')

        # Assert
        self.assertEqual(result['new_jobs'], 2)
        self.assertEqual(result['rejected'], 0)
        self.assertEqual(len(result['errors']), 0)
        mock_append.assert_any_call({'url': 'https://mockcompany.com/job1', 'title': 'Product Manager', 'company': 'MockCompany', 'location': 'NY', 'description': 'Full job description text'}, 'jobs-scraped')
        mock_append.assert_any_call({'url': 'https://mockcompany.com/job2', 'title': 'Product Owner', 'company': 'MockCompany', 'location': 'NY', 'description': 'Full job description text'}, 'jobs-scraped')

if __name__ == '__main__':
    unittest.main()
