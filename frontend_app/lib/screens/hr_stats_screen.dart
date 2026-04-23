import 'package:flutter/material.dart';
import '../services/api_service.dart';

class HrStatsScreen extends StatefulWidget {
  const HrStatsScreen({super.key});

  @override
  State<HrStatsScreen> createState() => _HrStatsScreenState();
}

class _HrStatsScreenState extends State<HrStatsScreen> {
  Map<String, dynamic>? _stats;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await ApiService.get('/applications/stats/');
      setState(() {
        _stats = data;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Статистика HR', style: TextStyle(fontWeight: FontWeight.w600)),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _stats == null
              ? const Center(child: Text('Ошибка загрузки'))
              : RefreshIndicator(
                  onRefresh: _load,
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _overviewCards(cs),
                        const SizedBox(height: 16),
                        _funnelCard(cs),
                        const SizedBox(height: 16),
                        _perJobCard(cs),
                      ],
                    ),
                  ),
                ),
    );
  }

  Widget _overviewCards(ColorScheme cs) {
    final s = _stats!;
    return Column(
      children: [
        Row(
          children: [
            _statTile('Всего откликов', '${s['total_applications'] ?? 0}', Icons.inbox, Colors.indigo),
            const SizedBox(width: 10),
            _statTile('За неделю', '${s['new_this_week'] ?? 0}', Icons.trending_up, Colors.green),
          ],
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            _statTile('Активных вакансий', '${s['active_jobs'] ?? 0}', Icons.work, Colors.blue),
            const SizedBox(width: 10),
            _statTile('Непрочитанных', '${s['unread_messages'] ?? 0}', Icons.chat, Colors.orange),
          ],
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            _statTile('За месяц', '${s['new_this_month'] ?? 0}', Icons.calendar_month, Colors.purple),
            const SizedBox(width: 10),
            _statTile('Ср. честность', '${s['avg_honesty'] ?? 0}%', Icons.verified, Colors.teal),
          ],
        ),
      ],
    );
  }

  Widget _statTile(String label, String value, IconData icon, Color color) {
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 40, height: 40,
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
                    Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: color)),
                    Text(label, style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _funnelCard(ColorScheme cs) {
    final funnel = _stats!['funnel'] ?? {};
    final total = funnel['total'] ?? 0;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.filter_alt, color: cs.primary),
                const SizedBox(width: 8),
                const Text('Воронка откликов', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
              ],
            ),
            const SizedBox(height: 16),
            _funnelBar('Всего', total, total, Colors.grey),
            _funnelBar('Ожидают', funnel['pending'] ?? 0, total, Colors.orange),
            _funnelBar('Просмотрено', funnel['reviewed'] ?? 0, total, Colors.blue),
            _funnelBar('Принято', funnel['accepted'] ?? 0, total, Colors.green),
            _funnelBar('Отклонено', funnel['rejected'] ?? 0, total, Colors.red),
            const SizedBox(height: 12),
            const Divider(),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _rateChip('Принятие', '${funnel['acceptance_rate'] ?? 0}%', Colors.green),
                _rateChip('Отказ', '${funnel['rejection_rate'] ?? 0}%', Colors.red),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _funnelBar(String label, int count, int total, Color color) {
    final pct = total > 0 ? count / total : 0.0;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: TextStyle(fontSize: 13, color: Colors.grey.shade700)),
              Text('$count', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: color)),
            ],
          ),
          const SizedBox(height: 4),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(value: pct, minHeight: 8, backgroundColor: Colors.grey.shade100, color: color),
          ),
        ],
      ),
    );
  }

  Widget _rateChip(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: color.withAlpha(20),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: color)),
          Text(label, style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
        ],
      ),
    );
  }

  Widget _perJobCard(ColorScheme cs) {
    final perJob = List<Map<String, dynamic>>.from(_stats!['per_job'] ?? []);
    if (perJob.isEmpty) return const SizedBox.shrink();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.list_alt, color: cs.primary),
                const SizedBox(width: 8),
                const Text('По вакансиям', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
              ],
            ),
            const SizedBox(height: 16),
            ...perJob.map((j) {
              final title = j['job__title'] ?? '';
              final total = j['total'] ?? 0;
              final pending = j['pending'] ?? 0;
              final accepted = j['accepted'] ?? 0;
              final rejected = j['rejected'] ?? 0;

              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade50,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        _miniStat('Всего', '$total', Colors.grey),
                        _miniStat('Ждут', '$pending', Colors.orange),
                        _miniStat('Принято', '$accepted', Colors.green),
                        _miniStat('Отказ', '$rejected', Colors.red),
                      ],
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _miniStat(String label, String value, Color color) {
    return Expanded(
      child: Column(
        children: [
          Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: color)),
          Text(label, style: TextStyle(fontSize: 10, color: Colors.grey.shade500)),
        ],
      ),
    );
  }
}
