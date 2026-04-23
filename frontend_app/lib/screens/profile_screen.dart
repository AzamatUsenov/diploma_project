import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/common.dart';

class ProfileScreen extends StatefulWidget {
  final VoidCallback onLogout;
  const ProfileScreen({required this.onLogout, super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _profile;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await ApiService.get('/accounts/profiles/me/');
      await ApiService.saveProfile(data);
      setState(() {
        _profile = data;
        _loading = false;
      });
    } catch (e) {
      final stored = await ApiService.getStoredProfile();
      setState(() {
        _profile = stored;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Профиль', style: TextStyle(fontWeight: FontWeight.w700)),
        centerTitle: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _confirmLogout,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _profile == null
              ? const Center(child: Text('Не удалось загрузить профиль'))
              : RefreshIndicator(
                  onRefresh: _load,
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        _profileHeader(cs),
                        const SizedBox(height: 16),
                        _infoCard(),
                        const SizedBox(height: 16),
                        _skillsCard(),
                        const SizedBox(height: 16),
                        _actionsCard(),
                      ],
                    ),
                  ),
                ),
    );
  }

  Widget _profileHeader(ColorScheme cs) {
    final p = _profile!;
    final role = p['role'] ?? 'applicant';
    final username = p['username'] ?? '';
    final email = p['email'] ?? '';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            CircleAvatar(
              radius: 40,
              backgroundColor: cs.primaryContainer,
              child: Text(
                username.isNotEmpty ? username[0].toUpperCase() : '?',
                style: TextStyle(fontSize: 32, fontWeight: FontWeight.w700, color: cs.primary),
              ),
            ),
            const SizedBox(height: 12),
            Text(username, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
            const SizedBox(height: 4),
            Text(email, style: TextStyle(fontSize: 14, color: Colors.grey.shade600)),
            const SizedBox(height: 8),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: (role == 'hr' ? Colors.orange : Colors.green).withAlpha(25),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    role == 'hr' ? 'HR менеджер' : 'Соискатель',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: role == 'hr' ? Colors.orange.shade700 : Colors.green.shade700,
                    ),
                  ),
                ),
                if (role == 'applicant' && p['level'] != null) ...[
                  const SizedBox(width: 8),
                  LevelBadge(p['level']),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _infoCard() {
    final p = _profile!;
    final role = p['role'] ?? 'applicant';

    final items = <(IconData, String, String)>[
      if (p['phone'] != null && (p['phone'] as String).isNotEmpty)
        (Icons.phone, 'Телефон', p['phone']),
      if (p['bio'] != null && (p['bio'] as String).isNotEmpty)
        (Icons.info_outline, 'О себе', p['bio']),
      if (role == 'applicant') ...[
        if (p['experience_years'] != null)
          (Icons.schedule, 'Опыт', '${p['experience_years']} лет'),
        if (p['education'] != null && (p['education'] as String).isNotEmpty)
          (Icons.school, 'Образование', p['education']),
      ],
      if (role == 'hr') ...[
        if (p['company'] != null && (p['company'] as String).isNotEmpty)
          (Icons.business, 'Компания', p['company']),
        if (p['position'] != null && (p['position'] as String).isNotEmpty)
          (Icons.badge, 'Должность', p['position']),
      ],
    ];

    if (items.isEmpty) return const SizedBox.shrink();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Информация', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
            const SizedBox(height: 12),
            ...items.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(item.$1, size: 18, color: Colors.grey.shade500),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(item.$2, style: TextStyle(fontSize: 11, color: Colors.grey.shade500)),
                        Text(item.$3, style: const TextStyle(fontSize: 14)),
                      ],
                    ),
                  ),
                ],
              ),
            )),
          ],
        ),
      ),
    );
  }

  Widget _skillsCard() {
    final skills = List<String>.from(_profile!['skills'] ?? []);
    if (skills.isEmpty) return const SizedBox.shrink();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Навыки', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
            const SizedBox(height: 12),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: skills.map((s) => SkillChip(s)).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _actionsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Настройки', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.edit),
              title: const Text('Редактировать профиль', style: TextStyle(fontSize: 14)),
              trailing: const Icon(Icons.chevron_right, size: 20),
              onTap: _editProfile,
            ),
            const Divider(height: 1),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.logout, color: Colors.red),
              title: const Text('Выйти', style: TextStyle(fontSize: 14, color: Colors.red)),
              onTap: _confirmLogout,
            ),
          ],
        ),
      ),
    );
  }

  void _editProfile() {
    final p = _profile!;
    final bioCtrl = TextEditingController(text: p['bio'] ?? '');
    final phoneCtrl = TextEditingController(text: p['phone'] ?? '');

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
            const Text('Редактировать профиль', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
            const SizedBox(height: 16),
            TextField(
              controller: phoneCtrl,
              decoration: const InputDecoration(labelText: 'Телефон'),
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: bioCtrl,
              decoration: const InputDecoration(labelText: 'О себе', alignLabelWithHint: true),
              maxLines: 3,
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: () async {
                  try {
                    await ApiService.patch('/accounts/profiles/me/', body: {
                      'bio': bioCtrl.text,
                      'phone': phoneCtrl.text,
                    });
                    if (ctx.mounted) Navigator.pop(ctx);
                    _load();
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Профиль обновлён')),
                      );
                    }
                  } catch (e) {
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Ошибка сохранения')),
                      );
                    }
                  }
                },
                child: const Text('Сохранить'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _confirmLogout() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Выйти?'),
        content: const Text('Вы уверены, что хотите выйти из аккаунта?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Отмена')),
          FilledButton(
            onPressed: () {
              Navigator.pop(ctx);
              widget.onLogout();
            },
            child: const Text('Выйти'),
          ),
        ],
      ),
    );
  }
}
