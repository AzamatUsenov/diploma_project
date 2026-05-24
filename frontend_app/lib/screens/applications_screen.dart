import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/common.dart';
import 'chat_screen.dart';
import 'hr_stats_screen.dart';

class ApplicationsScreen extends StatefulWidget {
  const ApplicationsScreen({super.key});

  @override
  State<ApplicationsScreen> createState() => _ApplicationsScreenState();
}

class _ApplicationsScreenState extends State<ApplicationsScreen> {
  List<dynamic> _applications = [];
  bool _loading = true;
  String? _role;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final profile = await ApiService.getStoredProfile();
      final data = await ApiService.get('/applications/');
      setState(() {
        _applications = data['results'] ?? [];
        _role = profile?['role'];
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'accepted':
        return Colors.green;
      case 'rejected':
        return Colors.red;
      case 'reviewed':
        return Colors.blue;
      default:
        return Colors.orange;
    }
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'accepted':
        return 'Принято';
      case 'rejected':
        return 'Отклонено';
      case 'reviewed':
        return 'Просмотрено';
      default:
        return 'Ожидает';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Заявки', style: TextStyle(fontWeight: FontWeight.w700)),
        centerTitle: false,
        actions: [
          if (_role == 'hr')
            IconButton(
              icon: const Icon(Icons.bar_chart),
              tooltip: 'Статистика',
              onPressed: () => Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const HrStatsScreen())),
            ),
        ],
      ),
      body: _loading
          ? ShimmerLoading.jobCards()
          : _applications.isEmpty
              ? const EmptyState(
                  icon: Icons.inbox_outlined,
                  title: 'Нет заявок',
                  subtitle: 'Ваши отклики появятся здесь',
                )
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _applications.length,
                    itemBuilder: (ctx, i) => _applicationCard(_applications[i]),
                  ),
                ),
    );
  }

  Widget _applicationCard(Map<String, dynamic> app) {
    final jobTitle = app['job_title'] ?? 'Вакансия';
    final jobCompany = app['job_company'] ?? '';
    final status = app['status'] ?? 'pending';
    final color = _statusColor(status);
    final createdAt = app['created_at'] ?? '';
    final appId = app['id'];
    final hintColor = Theme.of(context).hintColor;

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        onTap: () => Navigator.push(context,
            MaterialPageRoute(builder: (_) => ChatScreen(applicationId: appId, title: jobTitle))),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(jobTitle, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: color.withAlpha(25),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: color.withAlpha(60)),
                    ),
                    child: Text(_statusLabel(status),
                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: color)),
                  ),
                ],
              ),
              if (jobCompany.isNotEmpty) ...[
                const SizedBox(height: 6),
                Row(
                  children: [
                    Icon(Icons.business, size: 14, color: hintColor),
                    const SizedBox(width: 4),
                    Text(jobCompany, style: TextStyle(fontSize: 13, color: hintColor)),
                  ],
                ),
              ],
              if (app['cover_letter'] != null && (app['cover_letter'] as String).isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(app['cover_letter'],
                    style: TextStyle(fontSize: 13, color: hintColor),
                    maxLines: 2, overflow: TextOverflow.ellipsis),
              ],
              const SizedBox(height: 8),
              Row(
                children: [
                  if (createdAt.isNotEmpty)
                    Text(createdAt.length >= 10 ? createdAt.substring(0, 10) : createdAt,
                        style: TextStyle(fontSize: 12, color: hintColor)),
                  const Spacer(),
                  Icon(Icons.chat_bubble_outline, size: 16, color: hintColor),
                  const SizedBox(width: 4),
                  Text('Чат', style: TextStyle(fontSize: 12, color: hintColor)),
                ],
              ),
              if (_role == 'hr' && status == 'pending') ...[
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => _updateStatus(appId, 'rejected'),
                        style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
                        child: const Text('Отклонить'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: FilledButton(
                        onPressed: () => _updateStatus(appId, 'accepted'),
                        child: const Text('Принять'),
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _updateStatus(int id, String status) async {
    try {
      await ApiService.patch('/applications/$id/status/', body: {'status': status});
      _load();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Ошибка обновления')));
      }
    }
  }
}
