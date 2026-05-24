import 'package:flutter/material.dart';
import '../services/api_service.dart';

class NotificationsScreen extends StatefulWidget {
  final VoidCallback? onViewed;

  const NotificationsScreen({super.key, this.onViewed});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List<Map<String, dynamic>> _notifications = [];
  bool _loading = true;

  static const notifIcons = {
    'application_status': Icons.description,
    'new_message': Icons.chat_bubble_outline,
    'job_recommendation': Icons.work_outline,
    'test_result': Icons.check_circle_outline,
    'new_application': Icons.person_add,
  };

  static const notifColors = {
    'application_status': Color(0xFF2563EB),
    'new_message': Color(0xFF4F46E5),
    'job_recommendation': Color(0xFF10B981),
    'test_result': Color(0xFFA855F7),
    'new_application': Color(0xFFEC4899),
  };

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await ApiService.get('/notifications/', query: {'page_size': '50'});
      final notifs = <Map<String, dynamic>>[];

      if (data['results'] is List) {
        notifs.addAll((data['results'] as List).cast<Map<String, dynamic>>());
      }

      setState(() {
        _notifications = notifs;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Future<void> _markRead(int id) async {
    try {
      await ApiService.post('/notifications/$id/mark_read/', body: {});
      _load();
      widget.onViewed?.call();
    } catch (_) {}
  }

  Future<void> _markAllRead() async {
    try {
      await ApiService.post('/notifications/mark_all_read/', body: {});
      _load();
      widget.onViewed?.call();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Все уведомления прочитаны')),
        );
      }
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    final unreadCount = _notifications.where((n) => n['is_read'] != true).length;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          unreadCount > 0 ? 'Уведомления ($unreadCount)' : 'Уведомления',
          style: const TextStyle(fontWeight: FontWeight.w700),
        ),
        centerTitle: false,
        actions: [
          if (_notifications.any((n) => n['is_read'] != true))
            IconButton(
              icon: const Icon(Icons.done_all),
              onPressed: _markAllRead,
              tooltip: 'Прочитать все',
            ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _notifications.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.notifications_none, size: 64, color: Theme.of(context).hintColor.withAlpha(100)),
                      const SizedBox(height: 16),
                      Text('Нет уведомлений',
                          style: TextStyle(fontSize: 16, color: Theme.of(context).hintColor)),
                      const SizedBox(height: 8),
                      Text('Здесь появятся уведомления об откликах,\nсообщениях и результатах тестов',
                          style: TextStyle(fontSize: 13, color: Theme.of(context).hintColor.withAlpha(150)),
                          textAlign: TextAlign.center),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(12),
                    itemCount: _notifications.length,
                    itemBuilder: (ctx, i) => _buildNotificationCard(_notifications[i]),
                  ),
                ),
    );
  }

  Widget _buildNotificationCard(Map<String, dynamic> notif) {
    final type = notif['notification_type'] as String? ?? 'application_status';
    final icon = notifIcons[type] ?? Icons.notifications;
    final color = notifColors[type] ?? const Color(0xFF4F46E5);
    final isRead = notif['is_read'] as bool? ?? false;
    final cs = Theme.of(context).colorScheme;

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      color: isRead ? null : cs.primaryContainer.withAlpha(30),
      child: InkWell(
        onTap: () {
          if (!isRead) {
            _markRead(notif['id'] as int);
          }
        },
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withAlpha(25),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            notif['title'] as String? ?? '',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: isRead ? FontWeight.w500 : FontWeight.w700,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        if (!isRead)
                          Container(
                            width: 8,
                            height: 8,
                            margin: const EdgeInsets.only(left: 8),
                            decoration: BoxDecoration(
                              color: cs.primary,
                              borderRadius: BorderRadius.circular(4),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      notif['message'] as String? ?? '',
                      style: TextStyle(fontSize: 12, color: Theme.of(context).hintColor),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      notif['time_ago'] as String? ?? '',
                      style: TextStyle(fontSize: 11, color: Theme.of(context).hintColor),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
