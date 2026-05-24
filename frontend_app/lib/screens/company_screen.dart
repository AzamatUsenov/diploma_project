import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/common.dart';
import 'job_detail_screen.dart';

class CompanyScreen extends StatefulWidget {
  final String companyName;
  const CompanyScreen({required this.companyName, super.key});

  @override
  State<CompanyScreen> createState() => _CompanyScreenState();
}

class _CompanyScreenState extends State<CompanyScreen> {
  Map<String, dynamic>? _info;
  List<dynamic> _jobs = [];
  bool _loading = true;
  bool _isOwner = false;
  bool _editing = false;

  final _nameCtrl = TextEditingController();
  final _descCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _descCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final info = await ApiService.get('/jobs/company-info/', query: {'name': widget.companyName});
      final jobsData = await ApiService.get('/jobs/', query: {'company': widget.companyName});
      final profile = await ApiService.getStoredProfile();

      setState(() {
        _info = info;
        _jobs = (jobsData['results'] ?? []) as List;
        _isOwner = profile != null && info['hr_id'] == profile['user']?['id'];
        _nameCtrl.text = info['name'] ?? '';
        _descCtrl.text = info['description'] ?? '';
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Future<void> _save() async {
    try {
      await ApiService.patch('/accounts/profiles/me/', body: {
        'company_name': _nameCtrl.text,
        'company_description': _descCtrl.text,
      });
      setState(() => _editing = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Информация обновлена')),
      );
      _load();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Ошибка сохранения')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Text(_info?['name'] ?? widget.companyName, style: const TextStyle(fontWeight: FontWeight.w700)),
        actions: [
          if (_isOwner && !_editing)
            IconButton(
              icon: const Icon(Icons.edit_outlined),
              tooltip: 'Редактировать',
              onPressed: () => setState(() => _editing = true),
            ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _info == null
              ? const Center(child: Text('Компания не найдена'))
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      _buildHeader(cs),
                      if (_editing) ...[
                        const SizedBox(height: 16),
                        _buildEditForm(cs),
                      ],
                      const SizedBox(height: 24),
                      Text(
                        'Вакансии (${_jobs.length})',
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                      ),
                      const SizedBox(height: 12),
                      if (_jobs.isEmpty)
                        Card(
                          child: Padding(
                            padding: const EdgeInsets.all(24),
                            child: Center(
                              child: Text('Нет активных вакансий', style: TextStyle(color: cs.onSurfaceVariant)),
                            ),
                          ),
                        )
                      else
                        ..._jobs.map((job) => _jobCard(job)),
                    ],
                  ),
                ),
    );
  }

  Widget _buildHeader(ColorScheme cs) {
    final name = _info!['name'] ?? '';
    final description = _info!['description'] ?? '';
    final hrUsername = _info!['hr_username'];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: [cs.primary.withAlpha(40), cs.primary.withAlpha(80)]),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Center(
                child: Text(
                  name.isNotEmpty ? name[0].toUpperCase() : '?',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: cs.primary),
                ),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(name, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
                  const SizedBox(height: 4),
                  if (description.isNotEmpty)
                    Text(description, style: TextStyle(fontSize: 14, color: cs.onSurfaceVariant, height: 1.4))
                  else
                    Text('Описание не указано', style: TextStyle(fontSize: 14, color: cs.onSurfaceVariant, fontStyle: FontStyle.italic)),
                  if (hrUsername != null) ...[
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Icon(Icons.person_outline, size: 16, color: cs.onSurfaceVariant),
                        const SizedBox(width: 4),
                        Text('HR: $hrUsername', style: TextStyle(fontSize: 13, color: cs.onSurfaceVariant)),
                      ],
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEditForm(ColorScheme cs) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Редактировать', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
            const SizedBox(height: 12),
            TextField(
              controller: _nameCtrl,
              decoration: const InputDecoration(labelText: 'Название компании'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _descCtrl,
              decoration: const InputDecoration(labelText: 'Описание компании', alignLabelWithHint: true),
              maxLines: 4,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => setState(() => _editing = false),
                    child: const Text('Отмена'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: FilledButton(
                    onPressed: _save,
                    child: const Text('Сохранить'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _jobCard(Map<String, dynamic> job) {
    final techStack = List<String>.from(job['tech_stack'] ?? []);

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        onTap: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => JobDetailScreen(jobId: job['id'])),
        ),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(job['title'] ?? '', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                  ),
                  LevelBadge(job['level'] ?? 'junior'),
                ],
              ),
              const SizedBox(height: 6),
              Row(
                children: [
                  Text(job['location'] ?? '', style: TextStyle(fontSize: 13, color: Theme.of(context).hintColor)),
                  const SizedBox(width: 12),
                  SalaryText(min: job['salary_min'], max: job['salary_max']),
                ],
              ),
              if (techStack.isNotEmpty) ...[
                const SizedBox(height: 8),
                Wrap(
                  spacing: 4, runSpacing: 4,
                  children: techStack.take(4).map((t) => SkillChip(t)).toList(),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
