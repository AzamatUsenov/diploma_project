import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/common.dart';

class CompareScreen extends StatefulWidget {
  final List<int> jobIds;
  const CompareScreen({required this.jobIds, super.key});

  @override
  State<CompareScreen> createState() => _CompareScreenState();
}

class _CompareScreenState extends State<CompareScreen> {
  Map<String, dynamic>? _data;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await ApiService.post('/analytics/compare/', body: {
        'job_ids': widget.jobIds,
      });
      setState(() {
        _data = data;
        _loading = false;
      });
    } on ApiException catch (e) {
      setState(() {
        _error = e.message;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Ошибка загрузки';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Сравнение вакансий', style: TextStyle(fontWeight: FontWeight.w700)),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!, style: TextStyle(color: cs.error)))
              : _buildContent(cs),
    );
  }

  Widget _buildContent(ColorScheme cs) {
    final jobs = List<Map<String, dynamic>>.from(_data!['jobs'] ?? []);
    final comparison = _data!['comparison'] as Map<String, dynamic>? ?? {};
    final verdict = _data!['verdict'] as Map<String, dynamic>? ?? {};

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _verdictCard(verdict, jobs, cs),
          const SizedBox(height: 16),
          _scoresTable(jobs, comparison, cs),
          const SizedBox(height: 16),
          _detailCards(jobs, cs),
          const SizedBox(height: 16),
          _skillsComparison(jobs, comparison, cs),
        ],
      ),
    );
  }

  Widget _verdictCard(Map<String, dynamic> verdict, List<Map<String, dynamic>> jobs, ColorScheme cs) {
    final winnerId = verdict['winner_id'];
    final winner = jobs.firstWhere((j) => j['id'] == winnerId, orElse: () => jobs.first);
    final explanation = verdict['explanation'] ?? '';

    return Card(
      color: cs.primaryContainer.withAlpha(40),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.emoji_events, color: Colors.amber.shade700, size: 28),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    winner['title'] ?? '',
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              winner['company'] ?? '',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: Theme.of(context).hintColor),
            ),
            const SizedBox(height: 12),
            Text(explanation, style: const TextStyle(fontSize: 13, height: 1.5)),
          ],
        ),
      ),
    );
  }

  Widget _scoresTable(List<Map<String, dynamic>> jobs, Map<String, dynamic> comparison, ColorScheme cs) {
    final bestSalary = comparison['best_salary'];
    final mostHonest = comparison['most_honest'];
    final bestMatch = comparison['best_match'];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Сравнение по показателям', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
            const SizedBox(height: 16),
            _scoreRow('Общий балл', jobs, (j) => j['scores']?['overall_score'] ?? 0, null, cs),
            const Divider(height: 24),
            _scoreRow('Честность', jobs, (j) => j['scores']?['honesty_score'] ?? 0, mostHonest, cs),
            const Divider(height: 24),
            _scoreRow('Матч', jobs, (j) => j['scores']?['match_score'] ?? 0, bestMatch, cs),
            const Divider(height: 24),
            _salaryRow(jobs, bestSalary, cs),
            const Divider(height: 24),
            _boolRow('Обучение', jobs, (j) => j['training_provided'] == true, cs),
            const Divider(height: 24),
            _boolRow('Удалёнка', jobs, (j) => j['is_remote'] == true, cs),
          ],
        ),
      ),
    );
  }

  Widget _scoreRow(String label, List<Map<String, dynamic>> jobs, int Function(Map<String, dynamic>) getValue, int? bestId, ColorScheme cs) {
    final maxVal = jobs.map(getValue).reduce((a, b) => a > b ? a : b);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Theme.of(context).hintColor)),
        const SizedBox(height: 8),
        ...jobs.map((j) {
          final val = getValue(j);
          final isBest = bestId != null ? j['id'] == bestId : val == maxVal;
          final color = val >= 70 ? Colors.green : val >= 40 ? Colors.orange : Colors.red;
          return Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Row(
              children: [
                SizedBox(
                  width: 100,
                  child: Text(
                    _shortTitle(j['title'] ?? ''),
                    style: TextStyle(fontSize: 12, fontWeight: isBest ? FontWeight.w700 : FontWeight.w400),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Expanded(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: val / 100,
                      minHeight: 8,
                      backgroundColor: Colors.grey.withAlpha(30),
                      color: isBest ? color : color.withAlpha(150),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                SizedBox(
                  width: 40,
                  child: Text(
                    '$val%',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: color),
                    textAlign: TextAlign.right,
                  ),
                ),
                if (isBest) ...[
                  const SizedBox(width: 4),
                  Icon(Icons.star, size: 14, color: Colors.amber.shade700),
                ],
              ],
            ),
          );
        }),
      ],
    );
  }

  Widget _salaryRow(List<Map<String, dynamic>> jobs, int? bestId, ColorScheme cs) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Зарплата', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Theme.of(context).hintColor)),
        const SizedBox(height: 8),
        ...jobs.map((j) {
          final isBest = j['id'] == bestId;
          return Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Row(
              children: [
                SizedBox(
                  width: 100,
                  child: Text(
                    _shortTitle(j['title'] ?? ''),
                    style: TextStyle(fontSize: 12, fontWeight: isBest ? FontWeight.w700 : FontWeight.w400),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Expanded(
                  child: SalaryText(min: j['salary_min'], max: j['salary_max']),
                ),
                if (isBest) ...[
                  const SizedBox(width: 4),
                  Icon(Icons.star, size: 14, color: Colors.amber.shade700),
                ],
              ],
            ),
          );
        }),
      ],
    );
  }

  Widget _boolRow(String label, List<Map<String, dynamic>> jobs, bool Function(Map<String, dynamic>) getValue, ColorScheme cs) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Theme.of(context).hintColor)),
        const SizedBox(height: 8),
        ...jobs.map((j) {
          final val = getValue(j);
          return Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Row(
              children: [
                SizedBox(
                  width: 100,
                  child: Text(
                    _shortTitle(j['title'] ?? ''),
                    style: const TextStyle(fontSize: 12),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Icon(
                  val ? Icons.check_circle : Icons.cancel,
                  size: 18,
                  color: val ? Colors.green : Colors.red.shade300,
                ),
                const SizedBox(width: 6),
                Text(val ? 'Да' : 'Нет', style: TextStyle(fontSize: 13, color: val ? Colors.green : Colors.red.shade300)),
              ],
            ),
          );
        }),
      ],
    );
  }

  Widget _detailCards(List<Map<String, dynamic>> jobs, ColorScheme cs) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Подробности', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
        const SizedBox(height: 12),
        ...jobs.map((j) {
          final analysis = j['analysis'] as Map<String, dynamic>? ?? {};
          final match = j['match'] as Map<String, dynamic>?;
          final overqualified = analysis['is_overqualified'] == true;

          return Card(
            margin: const EdgeInsets.only(bottom: 10),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(j['title'] ?? '', style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
                      ),
                      LevelBadge(j['level'] ?? 'junior'),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(j['company'] ?? '', style: TextStyle(fontSize: 13, color: Theme.of(context).hintColor)),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      _miniChip('${analysis['honesty_score'] ?? 0}% честность',
                          (analysis['honesty_score'] ?? 0) >= 70 ? Colors.green : Colors.orange),
                      const SizedBox(width: 6),
                      _miniChip('Уровень: ${analysis['detected_level'] ?? '?'}', Colors.blueGrey),
                      if (overqualified) ...[
                        const SizedBox(width: 6),
                        _miniChip('Завышены', Colors.red),
                      ],
                    ],
                  ),
                  if (match != null) ...[
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        _miniChip('Матч: ${match['match_score']}%',
                            (match['match_score'] ?? 0) >= 70 ? Colors.green : Colors.orange),
                        const SizedBox(width: 6),
                        if (match['can_apply'] == true)
                          _miniChip('Подходит', Colors.green)
                        else
                          _miniChip('Стоит подтянуть', Colors.red),
                      ],
                    ),
                    if ((match['missing_skills'] as List?)?.isNotEmpty == true) ...[
                      const SizedBox(height: 8),
                      Text('Нужно изучить:', style: TextStyle(fontSize: 11, color: Colors.red.shade700, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 4),
                      Wrap(
                        spacing: 4, runSpacing: 4,
                        children: (match['missing_skills'] as List).take(5).map<Widget>(
                          (s) => SkillChip(s.toString(), color: Colors.red),
                        ).toList(),
                      ),
                    ],
                  ],
                ],
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _skillsComparison(List<Map<String, dynamic>> jobs, Map<String, dynamic> comparison, ColorScheme cs) {
    final commonSkills = List<String>.from(comparison['common_skills'] ?? []);
    final uniqueSkills = comparison['unique_skills'] as Map<String, dynamic>? ?? {};

    if (commonSkills.isEmpty && uniqueSkills.isEmpty) return const SizedBox.shrink();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Навыки', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
            if (commonSkills.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text('Общие для всех вакансий', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Theme.of(context).hintColor)),
              const SizedBox(height: 6),
              Wrap(
                spacing: 4, runSpacing: 4,
                children: commonSkills.map((s) => SkillChip(s, color: Colors.green)).toList(),
              ),
            ],
            ...jobs.map((j) {
              final unique = List<String>.from(uniqueSkills[j['id'].toString()] ?? []);
              if (unique.isEmpty) return const SizedBox.shrink();
              return Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Только в ${_shortTitle(j['title'] ?? '')}',
                        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Theme.of(context).hintColor)),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 4, runSpacing: 4,
                      children: unique.map((s) => SkillChip(s, color: cs.primary)).toList(),
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

  Widget _miniChip(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withAlpha(20),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(text, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: color)),
    );
  }

  String _shortTitle(String title) {
    return title.length > 15 ? '${title.substring(0, 15)}...' : title;
  }
}
