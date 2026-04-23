import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/common.dart';

class JobDetailScreen extends StatefulWidget {
  final int jobId;
  const JobDetailScreen({required this.jobId, super.key});

  @override
  State<JobDetailScreen> createState() => _JobDetailScreenState();
}

class _JobDetailScreenState extends State<JobDetailScreen> {
  Map<String, dynamic>? _job;
  Map<String, dynamic>? _analysis;
  Map<String, dynamic>? _match;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final job = await ApiService.get('/jobs/${widget.jobId}/');
      final analysis = await ApiService.get('/analytics/analyze/${widget.jobId}/');

      Map<String, dynamic>? match;
      final profile = await ApiService.getStoredProfile();
      if (profile != null && profile['role'] == 'applicant') {
        try {
          match = await ApiService.post('/analytics/match/', body: {'job_id': widget.jobId});
        } catch (_) {}
      }

      setState(() {
        _job = job;
        _analysis = analysis;
        _match = match;
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
        title: Text(_job?['title'] ?? 'Вакансия', style: const TextStyle(fontWeight: FontWeight.w600)),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _job == null
              ? const Center(child: Text('Ошибка загрузки'))
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _headerCard(),
                      const SizedBox(height: 12),
                      if (_analysis != null) _analysisCard(),
                      if (_match != null) ...[
                        const SizedBox(height: 12),
                        _matchCard(),
                      ],
                      const SizedBox(height: 12),
                      _descriptionCard(),
                      const SizedBox(height: 80),
                    ],
                  ),
                ),
      bottomSheet: _job != null ? _bottomBar() : null,
    );
  }

  Widget _headerCard() {
    final j = _job!;
    final techStack = List<String>.from(j['tech_stack'] ?? []);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(child: Text(j['title'], style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800))),
                LevelBadge(j['level']),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                const Icon(Icons.business, size: 16, color: Colors.grey),
                const SizedBox(width: 6),
                Text(j['company'], style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)),
                const SizedBox(width: 16),
                const Icon(Icons.location_on_outlined, size: 16, color: Colors.grey),
                const SizedBox(width: 4),
                Text(j['location'] ?? '', style: TextStyle(color: Colors.grey.shade600)),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                SalaryText(min: j['salary_min'], max: j['salary_max']),
                const SizedBox(width: 16),
                Text('${j['experience_years']} лет опыта', style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
                if (j['is_remote'] == true) ...[
                  const SizedBox(width: 12),
                  const SkillChip('Remote', color: Colors.indigo),
                ],
                if (j['training_provided'] == true) ...[
                  const SizedBox(width: 8),
                  const SkillChip('Обучение', color: Colors.green),
                ],
              ],
            ),
            if (techStack.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 6, runSpacing: 6,
                children: techStack.map((t) => SkillChip(t)).toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _analysisCard() {
    final a = _analysis!;
    final honesty = a['honesty_score'] ?? 0;
    final honestyColor = honesty >= 70 ? Colors.green : honesty >= 40 ? Colors.orange : Colors.red;
    final parsedSkills = List<String>.from(a['parsed_skills'] ?? []);
    final skillsByLevel = a['skills_by_level'] ?? {};

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.analytics, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 8),
                const Text('Анализ вакансии', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
              ],
            ),
            const SizedBox(height: 16),

            // Stats grid
            Row(
              children: [
                _statBox('$honesty%', 'Честность', honestyColor),
                const SizedBox(width: 8),
                _statBox(a['detected_level'] ?? '?', 'Реальный уровень', Colors.blueGrey),
                const SizedBox(width: 8),
                _statBox('${parsedSkills.length}', 'Навыков', Colors.indigo),
                const SizedBox(width: 8),
                _statBox(
                  a['is_overqualified'] == true ? '⚠' : '✓',
                  a['is_overqualified'] == true ? 'Завышены' : 'Адекватные',
                  a['is_overqualified'] == true ? Colors.red : Colors.green,
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Skills by level
            for (final entry in [('junior', 'Junior', Colors.green), ('mid', 'Middle', Colors.blue), ('senior', 'Senior', Colors.purple)])
              if (skillsByLevel[entry.$1] != null && (skillsByLevel[entry.$1] as List).isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SizedBox(
                        width: 55,
                        child: Text(entry.$2, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: entry.$3.shade700)),
                      ),
                      Expanded(
                        child: Wrap(
                          spacing: 4, runSpacing: 4,
                          children: (skillsByLevel[entry.$1] as List).map<Widget>((s) => SkillChip(s.toString(), color: entry.$3)).toList(),
                        ),
                      ),
                    ],
                  ),
                ),
          ],
        ),
      ),
    );
  }

  Widget _statBox(String value, String label, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: color.withAlpha(20),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: color)),
            const SizedBox(height: 4),
            Text(label, style: TextStyle(fontSize: 10, color: Colors.grey.shade600), textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }

  Widget _matchCard() {
    final m = _match!;
    final score = m['match_score'] ?? 0;
    final scoreColor = score >= 70 ? Colors.green : score >= 40 ? Colors.orange : Colors.red;
    final matching = List<String>.from(m['matching_skills'] ?? []);
    final missing = List<String>.from(m['missing_skills'] ?? []);
    final learningPath = List<String>.from(m['learning_path'] ?? []);
    final canApply = m['can_apply'] == true;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.verified_user, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 8),
                const Text('Ваш матч', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
              ],
            ),
            const SizedBox(height: 16),

            // Score circle
            Center(
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 100, height: 100,
                    child: CircularProgressIndicator(
                      value: score / 100,
                      strokeWidth: 8,
                      backgroundColor: Colors.grey.shade200,
                      color: scoreColor,
                    ),
                  ),
                  Text('$score%', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: scoreColor.shade700)),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Center(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: (canApply ? Colors.green : Colors.red).withAlpha(25),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  canApply ? '✓ Рекомендуем подавать' : '✗ Стоит подтянуть навыки',
                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: canApply ? Colors.green.shade700 : Colors.red.shade700),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Text(m['recommendation'] ?? '', style: TextStyle(fontSize: 13, color: Colors.grey.shade600), textAlign: TextAlign.center),
            const SizedBox(height: 16),

            // Skills
            if (matching.isNotEmpty) ...[
              Text('Совпадающие (${matching.length})', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.green.shade700)),
              const SizedBox(height: 6),
              Wrap(spacing: 4, runSpacing: 4, children: matching.map((s) => SkillChip(s, color: Colors.green)).toList()),
              const SizedBox(height: 12),
            ],
            if (missing.isNotEmpty) ...[
              Text('Нужно изучить (${missing.length})', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.red.shade700)),
              const SizedBox(height: 6),
              Wrap(spacing: 4, runSpacing: 4, children: missing.map((s) => SkillChip(s, color: Colors.red)).toList()),
            ],

            if (learningPath.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 8),
              const Text('План обучения', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              ...learningPath.asMap().entries.map((e) => Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    CircleAvatar(radius: 12, backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                      child: Text('${e.key + 1}', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.primary))),
                    const SizedBox(width: 10),
                    Expanded(child: Text(e.value, style: TextStyle(fontSize: 13, color: Colors.grey.shade700))),
                  ],
                ),
              )),
            ],
          ],
        ),
      ),
    );
  }

  Widget _descriptionCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Описание', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
            const SizedBox(height: 12),
            Text(_job!['description'] ?? '', style: TextStyle(fontSize: 14, color: Colors.grey.shade700, height: 1.5)),
            const SizedBox(height: 16),
            const Text('Требования', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            Text(_job!['requirements_text'] ?? '', style: TextStyle(fontSize: 14, color: Colors.grey.shade700, height: 1.5)),
          ],
        ),
      ),
    );
  }

  Widget _bottomBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [BoxShadow(color: Colors.black.withAlpha(10), blurRadius: 10, offset: const Offset(0, -2))],
      ),
      child: Row(
        children: [
          Expanded(
            child: OutlinedButton.icon(
              onPressed: _addToFavorites,
              icon: const Icon(Icons.favorite_border, size: 18),
              label: const Text('Избранное'),
              style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 14)),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            flex: 2,
            child: FilledButton.icon(
              onPressed: _showApplyDialog,
              icon: const Icon(Icons.send, size: 18),
              label: const Text('Откликнуться'),
              style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 14)),
            ),
          ),
        ],
      ),
    );
  }

  void _addToFavorites() async {
    try {
      await ApiService.post('/analytics/favorites/', body: {'job_id': widget.jobId});
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Добавлено в избранное!')));
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Уже в избранном')));
    }
  }

  void _showApplyDialog() {
    final letterCtrl = TextEditingController();
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => Padding(
        padding: EdgeInsets.fromLTRB(24, 24, 24, MediaQuery.of(ctx).viewInsets.bottom + 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Откликнуться', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
            const SizedBox(height: 4),
            Text('${_job!['title']} — ${_job!['company']}', style: TextStyle(color: Colors.grey.shade600, fontSize: 14)),
            const SizedBox(height: 16),
            TextField(
              controller: letterCtrl,
              decoration: const InputDecoration(
                labelText: 'Сопроводительное письмо',
                hintText: 'Расскажите, почему вы подходите...',
                alignLabelWithHint: true,
              ),
              maxLines: 4,
            ),
            const SizedBox(height: 6),
            Text('Необязательно, но повышает шансы', style: TextStyle(fontSize: 12, color: Colors.grey.shade500)),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: () async {
                  try {
                    await ApiService.post('/applications/', body: {
                      'job': widget.jobId,
                      'cover_letter': letterCtrl.text,
                    });
                    if (ctx.mounted) Navigator.pop(ctx);
                    if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Отклик отправлен!')));
                  } on ApiException catch (e) {
                    if (ctx.mounted) Navigator.pop(ctx);
                    if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
                  }
                },
                child: const Text('Отправить отклик'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
