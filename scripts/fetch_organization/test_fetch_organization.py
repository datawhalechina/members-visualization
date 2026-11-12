import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fetch_organization import CONFIG, fetch_organization_data, fetch_top_knowledge_sharing_organization_data


class FetchTopOrganizationRankingTest(unittest.TestCase):
    def test_uses_cached_ranking_when_refresh_fails(self):
        ranking = [{'name': 'datawhalechina', 'star_count': 123, 'rank': 7}]
        with tempfile.TemporaryDirectory() as directory:
            data_dir = Path(directory) / 'data'
            organization_dir = data_dir / 'organization'
            repo_dir = data_dir / 'repo'
            organization_dir.mkdir(parents=True)
            (organization_dir / 'repo_list.json').write_text('[]', encoding='utf-8')
            cached_ranking = organization_dir / 'top_10_knowledge_sharing_organization.json'
            cached_ranking.write_text(json.dumps(ranking), encoding='utf-8')
            with patch.dict(CONFIG, {
                    'DATA_DIR': data_dir,
                    'ORGANIZATION_DATA_DIR': organization_dir,
                    'REPO_DATA_DIR': repo_dir,
            }), patch('fetch_organization.fetch_organization_from_star_history',
                      side_effect=RuntimeError('ranking service unavailable')), \
                    patch('fetch_organization.fetch_organization_repo_detail',
                          return_value={'repo_list': [], 'repo_detail_list': []}):
                fetch_organization_data('2026-11')

            monthly_ranking = organization_dir / '2026-11' / cached_ranking.name
            self.assertEqual(json.loads(monthly_ranking.read_text(encoding='utf-8')), ranking)
            self.assertEqual(json.loads(cached_ranking.read_text(encoding='utf-8')), ranking)

    def test_refresh_failure_without_cache_still_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            cache_path = Path(directory) / 'ranking.json'
            with patch('fetch_organization.fetch_organization_from_star_history',
                       side_effect=RuntimeError('ranking service unavailable')):
                with self.assertRaisesRegex(RuntimeError, 'ranking service unavailable'):
                    fetch_top_knowledge_sharing_organization_data(cache_path)


if __name__ == '__main__':
    unittest.main()
