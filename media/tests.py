from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Media


class MediaModelTest(TestCase):
    """Test cases for Media model"""
    
    def setUp(self):
        """Set up test data"""
        self.media_data = {
            'title': 'Test Image',
            'description': 'A test image',
            'media_type': 'image',
            'uploaded_by': 'test_user'
        }
    
    def test_create_media(self):
        """Test creating a media instance"""
        media = Media.objects.create(**self.media_data)
        self.assertEqual(media.title, 'Test Image')
        self.assertEqual(media.media_type, 'image')
        self.assertTrue(media.is_active)
    
    def test_media_str(self):
        """Test media string representation"""
        media = Media.objects.create(**self.media_data)
        self.assertEqual(str(media), 'Test Image')
    
    def test_media_default_is_active(self):
        """Test that media is active by default"""
        media = Media.objects.create(**self.media_data)
        self.assertTrue(media.is_active)


class MediaAPITest(APITestCase):
    """Test cases for Media API endpoints"""
    
    def setUp(self):
        """Set up test data and authentication"""
        self.media = Media.objects.create(
            title='API Test Media',
            media_type='image',
            uploaded_by='api_user'
        )
    
    def test_list_media(self):
        """Test listing all media files"""
        url = reverse('media-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_retrieve_media(self):
        """Test retrieving a single media file"""
        url = reverse('media-detail', kwargs={'pk': self.media.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'API Test Media')
    
    def test_create_media(self):
        """Test creating a new media file"""
        url = reverse('media-list')
        data = {
            'title': 'New Media',
            'media_type': 'video',
            'uploaded_by': 'new_user'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Media.objects.count(), 2)
    
    def test_update_media(self):
        """Test updating a media file"""
        url = reverse('media-detail', kwargs={'pk': self.media.pk})
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.media.refresh_from_db()
        self.assertEqual(self.media.title, 'Updated Title')
    
    def test_delete_media(self):
        """Test deleting a media file (soft delete)"""
        url = reverse('media-detail', kwargs={'pk': self.media.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.media.refresh_from_db()
        self.assertFalse(self.media.is_active)
    
    def test_upload_action(self):
        """Test custom upload action"""
        url = reverse('media-upload')
        response = self.client.post(url, {'title': 'Uploaded File'}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_by_media_type(self):
        """Test filtering media by type"""
        url = reverse('media-list')
        response = self.client.get(url, {'media_type': 'image'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_download_action(self):
        """Test download action"""
        url = reverse('media-download', kwargs={'pk': self.media.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('download_url', response.data)
