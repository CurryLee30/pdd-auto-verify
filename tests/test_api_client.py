"""
API客户端测试
"""
import unittest
from unittest.mock import Mock, patch
import requests

from core.api_client import PddAPIClient
from core.exceptions import APIException


class TestPddAPIClient(unittest.TestCase):
    """拼多多API客户端测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = PddAPIClient()
    
    def test_generate_signature(self):
        """测试签名生成"""
        params = {
            "type": "test",
            "client_id": "test_id",
            "timestamp": "1234567890"
        }
        
        signature = self.client._generate_signature(params)
        self.assertIsInstance(signature, str)
        self.assertEqual(len(signature), 32)  # MD5签名长度
    
    def test_prepare_request_params(self):
        """测试请求参数准备"""
        method = "test.method"
        params = {"test_param": "test_value"}
        
        request_params = self.client._prepare_request_params(method, params)
        
        self.assertIn("type", request_params)
        self.assertIn("client_id", request_params)
        self.assertIn("access_token", request_params)
        self.assertIn("timestamp", request_params)
        self.assertIn("sign", request_params)
        self.assertIn("test_param", request_params)
    
    @patch('requests.post')
    def test_make_request_success(self, mock_post):
        """测试API请求成功"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "test_response": {
                "success": True
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client._make_request("test.method", {"test": "value"})
        
        self.assertIn("test_response", result)
        self.assertTrue(result["test_response"]["success"])
    
    @patch('requests.post')
    def test_make_request_error(self, mock_post):
        """测试API请求错误"""
        # 模拟错误响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "error_response": {
                "error_msg": "测试错误"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with self.assertRaises(APIException):
            self.client._make_request("test.method", {"test": "value"})
    
    @patch('requests.post')
    def test_make_request_network_error(self, mock_post):
        """测试网络错误"""
        # 模拟网络错误
        mock_post.side_effect = requests.exceptions.RequestException("网络错误")
        
        with self.assertRaises(APIException):
            self.client._make_request("test.method", {"test": "value"})


if __name__ == "__main__":
    unittest.main()
