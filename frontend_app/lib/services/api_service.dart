import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://10.0.2.2:8000/api';

  static Future<String?> _getAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  static Future<void> _saveTokens(String access, String refresh) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', access);
    await prefs.setString('refresh_token', refresh);
  }

  static Future<void> saveProfile(Map<String, dynamic> profile) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('profile', jsonEncode(profile));
  }

  static Future<Map<String, dynamic>?> getStoredProfile() async {
    final prefs = await SharedPreferences.getInstance();
    final s = prefs.getString('profile');
    if (s == null) return null;
    return jsonDecode(s);
  }

  static Future<bool> isLoggedIn() async {
    final token = await _getAccessToken();
    return token != null;
  }

  static Future<void> clearAuth() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    await prefs.remove('profile');
  }

  static Future<bool> _refreshToken() async {
    final prefs = await SharedPreferences.getInstance();
    final refresh = prefs.getString('refresh_token');
    if (refresh == null) return false;
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/accounts/token/refresh/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh': refresh}),
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        await prefs.setString('access_token', data['access']);
        return true;
      }
    } catch (_) {}
    await clearAuth();
    return false;
  }

  static Future<Map<String, dynamic>> request(
    String method,
    String path, {
    Map<String, dynamic>? body,
    Map<String, String>? queryParams,
  }) async {
    var url = Uri.parse('$baseUrl$path');
    if (queryParams != null) {
      url = url.replace(queryParameters: queryParams);
    }

    final token = await _getAccessToken();
    final headers = <String, String>{
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };

    http.Response res;
    switch (method) {
      case 'POST':
        res = await http.post(url, headers: headers, body: body != null ? jsonEncode(body) : null);
        break;
      case 'PATCH':
        res = await http.patch(url, headers: headers, body: body != null ? jsonEncode(body) : null);
        break;
      case 'DELETE':
        res = await http.delete(url, headers: headers);
        break;
      default:
        res = await http.get(url, headers: headers);
    }

    if (res.statusCode == 401 && token != null) {
      final refreshed = await _refreshToken();
      if (refreshed) {
        return request(method, path, body: body, queryParams: queryParams);
      }
      throw ApiException(401, 'Сессия истекла');
    }

    if (res.statusCode == 204) return {};

    final data = res.body.isNotEmpty ? jsonDecode(utf8.decode(res.bodyBytes)) : {};
    if (res.statusCode >= 400) {
      throw ApiException(res.statusCode, data is Map ? data : {'detail': 'Ошибка'});
    }
    return data is Map<String, dynamic> ? data : {'data': data};
  }

  static Future<Map<String, dynamic>> get(String path, {Map<String, String>? query}) =>
      request('GET', path, queryParams: query);

  static Future<Map<String, dynamic>> post(String path, {Map<String, dynamic>? body}) =>
      request('POST', path, body: body);

  static Future<Map<String, dynamic>> patch(String path, {Map<String, dynamic>? body}) =>
      request('PATCH', path, body: body);

  static Future<Map<String, dynamic>> delete(String path) =>
      request('DELETE', path);

  static Future<Map<String, dynamic>> uploadResume(File file) async {
    final token = await _getAccessToken();
    final uri = Uri.parse('$baseUrl/accounts/profiles/upload-resume/');
    final req = http.MultipartRequest('POST', uri);
    if (token != null) req.headers['Authorization'] = 'Bearer $token';
    req.files.add(await http.MultipartFile.fromPath('resume', file.path));
    final streamed = await req.send();
    final res = await http.Response.fromStream(streamed);
    if (res.statusCode == 401) throw ApiException(401, 'Сессия истекла');
    final data = res.body.isNotEmpty ? jsonDecode(utf8.decode(res.bodyBytes)) : {};
    if (res.statusCode >= 400) throw ApiException(res.statusCode, data is Map ? data : {'detail': 'Ошибка'});
    return data is Map<String, dynamic> ? data : {'data': data};
  }

  // Auth
  static Future<Map<String, dynamic>> login(String username, String password) async {
    final data = await post('/accounts/login/', body: {
      'username': username,
      'password': password,
    });
    await _saveTokens(data['tokens']['access'], data['tokens']['refresh']);
    await saveProfile(data['user']);
    return data;
  }

  static Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    required String role,
    String level = 'junior',
  }) async {
    final body = <String, dynamic>{
      'username': username,
      'email': email,
      'password': password,
      'role': role,
    };
    if (role == 'applicant') body['level'] = level;
    final data = await post('/accounts/register/', body: body);
    await _saveTokens(data['tokens']['access'], data['tokens']['refresh']);
    await saveProfile(data['user']);
    return data;
  }
}

class ApiException implements Exception {
  final int statusCode;
  final dynamic data;

  ApiException(this.statusCode, this.data);

  String get message {
    if (data is Map) {
      if (data.containsKey('detail')) return data['detail'].toString();
      if (data.containsKey('username')) return data['username'][0].toString();
      if (data.containsKey('non_field_errors')) return data['non_field_errors'][0].toString();
      return data.values.first.toString();
    }
    return data.toString();
  }
}
