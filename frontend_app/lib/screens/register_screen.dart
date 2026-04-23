import 'package:flutter/material.dart';
import '../services/api_service.dart';

class RegisterScreen extends StatefulWidget {
  final VoidCallback onRegisterSuccess;
  const RegisterScreen({required this.onRegisterSuccess, super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _usernameCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  String _role = 'applicant';
  String _level = 'junior';
  bool _loading = false;
  bool _obscure = true;
  String? _error;

  Future<void> _register() async {
    if (_usernameCtrl.text.isEmpty || _emailCtrl.text.isEmpty || _passwordCtrl.text.isEmpty) {
      setState(() => _error = 'Заполните все поля');
      return;
    }
    if (_passwordCtrl.text.length < 6) {
      setState(() => _error = 'Пароль минимум 6 символов');
      return;
    }
    setState(() { _loading = true; _error = null; });
    try {
      await ApiService.register(
        username: _usernameCtrl.text.trim(),
        email: _emailCtrl.text.trim(),
        password: _passwordCtrl.text,
        role: _role,
        level: _level,
      );
      if (mounted) {
        widget.onRegisterSuccess();
        Navigator.of(context).pop();
      }
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = 'Ошибка подключения к серверу');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(title: const Text('Регистрация')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Создайте аккаунт', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: cs.onSurface)),
            const SizedBox(height: 24),

            // Role
            Text('Кто вы?', style: TextStyle(fontWeight: FontWeight.w600, color: Colors.grey.shade700)),
            const SizedBox(height: 8),
            Row(
              children: [
                _roleCard('applicant', 'Соискатель', Icons.person, Colors.green),
                const SizedBox(width: 12),
                _roleCard('hr', 'HR менеджер', Icons.business, Colors.orange),
              ],
            ),
            const SizedBox(height: 20),

            TextField(
              controller: _usernameCtrl,
              decoration: const InputDecoration(labelText: 'Имя пользователя'),
              textInputAction: TextInputAction.next,
            ),
            const SizedBox(height: 14),
            TextField(
              controller: _emailCtrl,
              decoration: const InputDecoration(labelText: 'Email'),
              keyboardType: TextInputType.emailAddress,
              textInputAction: TextInputAction.next,
            ),
            const SizedBox(height: 14),
            TextField(
              controller: _passwordCtrl,
              decoration: InputDecoration(
                labelText: 'Пароль',
                suffixIcon: IconButton(
                  icon: Icon(_obscure ? Icons.visibility_off : Icons.visibility),
                  onPressed: () => setState(() => _obscure = !_obscure),
                ),
              ),
              obscureText: _obscure,
            ),
            const SizedBox(height: 20),

            if (_role == 'applicant') ...[
              Text('Ваш уровень', style: TextStyle(fontWeight: FontWeight.w600, color: Colors.grey.shade700)),
              const SizedBox(height: 8),
              Row(
                children: [
                  _levelChip('junior', 'Junior', '🌱'),
                  const SizedBox(width: 8),
                  _levelChip('mid', 'Middle', '💻'),
                  const SizedBox(width: 8),
                  _levelChip('senior', 'Senior', '🚀'),
                ],
              ),
              const SizedBox(height: 20),
            ],

            if (_error != null)
              Container(
                width: double.infinity,
                margin: const EdgeInsets.only(bottom: 16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: cs.errorContainer, borderRadius: BorderRadius.circular(12)),
                child: Text(_error!, style: TextStyle(fontSize: 13, color: cs.error)),
              ),

            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: _loading ? null : _register,
                child: _loading
                    ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Text('Создать аккаунт', style: TextStyle(fontSize: 16)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _roleCard(String value, String label, IconData icon, MaterialColor color) {
    final selected = _role == value;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _role = value),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: selected ? color.withAlpha(25) : Colors.grey.shade50,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: selected ? color : Colors.grey.shade300, width: selected ? 2 : 1),
          ),
          child: Column(
            children: [
              Icon(icon, color: selected ? color.shade700 : Colors.grey, size: 32),
              const SizedBox(height: 8),
              Text(label, style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13, color: selected ? color.shade700 : Colors.grey.shade600)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _levelChip(String value, String label, String emoji) {
    final selected = _level == value;
    final cs = Theme.of(context).colorScheme;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _level = value),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: selected ? cs.primaryContainer : Colors.grey.shade50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: selected ? cs.primary : Colors.grey.shade300, width: selected ? 2 : 1),
          ),
          child: Column(
            children: [
              Text(emoji, style: const TextStyle(fontSize: 20)),
              const SizedBox(height: 4),
              Text(label, style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12, color: selected ? cs.primary : Colors.grey.shade600)),
            ],
          ),
        ),
      ),
    );
  }
}
