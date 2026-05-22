import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class OnboardingScreen extends StatefulWidget {
  final VoidCallback onComplete;
  const OnboardingScreen({required this.onComplete, super.key});

  static Future<bool> shouldShow() async {
    final prefs = await SharedPreferences.getInstance();
    return !(prefs.getBool('onboarding_seen') ?? false);
  }

  static Future<void> markSeen() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('onboarding_seen', true);
  }

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final _controller = PageController();
  int _page = 0;

  static const _pages = [
    _PageData(
      icon: Icons.work_outline,
      color: Color(0xFF4F46E5),
      title: 'Честные вакансии',
      subtitle: 'Мы анализируем требования и показываем реальный уровень каждой вакансии. '
          'Никаких "Junior с 5-летним опытом".',
    ),
    _PageData(
      icon: Icons.analytics_outlined,
      color: Color(0xFF10B981),
      title: 'Умный матчинг',
      subtitle: 'Платформа сравнивает ваши навыки с требованиями и подсказывает, '
          'куда стоит откликнуться и что подтянуть.',
    ),
    _PageData(
      icon: Icons.quiz_outlined,
      color: Color(0xFFA855F7),
      title: 'Тесты навыков',
      subtitle: 'Проходите тесты, подтверждайте свой уровень и повышайте шансы '
          'получить работу мечты.',
    ),
  ];

  void _next() {
    if (_page < _pages.length - 1) {
      _controller.nextPage(duration: const Duration(milliseconds: 400), curve: Curves.easeOutCubic);
    } else {
      _finish();
    }
  }

  void _finish() {
    OnboardingScreen.markSeen();
    widget.onComplete();
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Align(
              alignment: Alignment.topRight,
              child: TextButton(
                onPressed: _finish,
                child: Text('Пропустить', style: TextStyle(color: cs.onSurfaceVariant)),
              ),
            ),
            Expanded(
              child: PageView.builder(
                controller: _controller,
                itemCount: _pages.length,
                onPageChanged: (i) => setState(() => _page = i),
                itemBuilder: (ctx, i) => _buildPage(_pages[i]),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(32, 0, 32, 40),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(_pages.length, (i) => AnimatedContainer(
                      duration: const Duration(milliseconds: 300),
                      margin: const EdgeInsets.symmetric(horizontal: 4),
                      width: _page == i ? 24 : 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: _page == i ? cs.primary : cs.primary.withAlpha(50),
                        borderRadius: BorderRadius.circular(4),
                      ),
                    )),
                  ),
                  const SizedBox(height: 32),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton(
                      onPressed: _next,
                      style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
                      child: Text(
                        _page < _pages.length - 1 ? 'Далее' : 'Начать',
                        style: const TextStyle(fontSize: 16),
                      ),
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

  Widget _buildPage(_PageData data) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 40),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              color: data.color.withAlpha(25),
              borderRadius: BorderRadius.circular(32),
            ),
            child: Icon(data.icon, size: 56, color: data.color),
          ),
          const SizedBox(height: 40),
          Text(
            data.title,
            style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w800),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          Text(
            data.subtitle,
            style: TextStyle(fontSize: 15, color: Theme.of(context).hintColor, height: 1.5),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _PageData {
  final IconData icon;
  final Color color;
  final String title;
  final String subtitle;
  const _PageData({required this.icon, required this.color, required this.title, required this.subtitle});
}
