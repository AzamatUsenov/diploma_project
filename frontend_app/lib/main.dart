import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'services/api_service.dart';
import 'services/theme_service.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/jobs_screen.dart';
import 'screens/job_detail_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/applications_screen.dart';
import 'screens/tests_screen.dart';
import 'screens/notifications_screen.dart';
import 'screens/onboarding_screen.dart';
import 'screens/reviews_screen.dart';
import 'screens/live_coding_screen.dart';
import 'screens/calendar_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await ThemeService().load();
  final showOnboarding = await OnboardingScreen.shouldShow();
  runApp(JobPlatformApp(showOnboarding: showOnboarding));
}

class JobPlatformApp extends StatefulWidget {
  final bool showOnboarding;
  const JobPlatformApp({super.key, this.showOnboarding = false});

  @override
  State<JobPlatformApp> createState() => _JobPlatformAppState();
}

class _JobPlatformAppState extends State<JobPlatformApp> {
  final _theme = ThemeService();
  late bool _showOnboarding;

  @override
  void initState() {
    super.initState();
    _showOnboarding = widget.showOnboarding;
    _theme.addListener(_onThemeChange);
  }

  @override
  void dispose() {
    _theme.removeListener(_onThemeChange);
    super.dispose();
  }

  void _onThemeChange() => setState(() {});

  static const _seedColor = Color(0xFF4F46E5);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JobPlatform',
      debugShowCheckedModeBanner: false,
      locale: const Locale('ru'),
      supportedLocales: const [Locale('ru')],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      themeMode: _theme.mode,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: _seedColor,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        fontFamily: 'Segoe UI',
        appBarTheme: AppBarTheme(
          scrolledUnderElevation: 0.5,
          backgroundColor: Colors.white.withAlpha(220),
          surfaceTintColor: Colors.transparent,
          shadowColor: Colors.black.withAlpha(15),
        ),
        cardTheme: CardThemeData(
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: BorderSide(color: Colors.grey.shade200),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
        ),
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: _seedColor,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
        fontFamily: 'Segoe UI',
        appBarTheme: AppBarTheme(
          scrolledUnderElevation: 0.5,
          backgroundColor: const Color(0xFF1C1C1E).withAlpha(220),
          surfaceTintColor: Colors.transparent,
          shadowColor: Colors.black.withAlpha(30),
          foregroundColor: Colors.white,
          titleTextStyle: const TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.w700,
            fontFamily: 'Segoe UI',
          ),
          iconTheme: const IconThemeData(color: Colors.white),
        ),
        cardTheme: CardThemeData(
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: BorderSide(color: Colors.grey.shade800),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
        ),
      ),
      home: _showOnboarding
          ? OnboardingScreen(onComplete: () => setState(() => _showOnboarding = false))
          : const AppShell(),
    );
  }
}

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _currentIndex = 0;
  bool _loggedIn = false;
  Map<String, dynamic>? _profile;
  int _unreadCount = 0;
  Timer? _unreadTimer;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  @override
  void dispose() {
    _unreadTimer?.cancel();
    super.dispose();
  }

  Future<void> _checkAuth() async {
    final loggedIn = await ApiService.isLoggedIn();
    final profile = await ApiService.getStoredProfile();
    if (mounted) {
      setState(() {
        _loggedIn = loggedIn;
        _profile = profile;
      });
      if (loggedIn) {
        _fetchUnreadCount();
        _unreadTimer?.cancel();
        _unreadTimer = Timer.periodic(const Duration(seconds: 30), (_) => _fetchUnreadCount());
      }
    }
  }

  Future<void> _fetchUnreadCount() async {
    try {
      final data = await ApiService.get('/notifications/unread_count/');
      if (mounted) setState(() => _unreadCount = data['count'] ?? 0);
    } catch (_) {}
  }

  void _onLoginSuccess() {
    _checkAuth();
    setState(() => _currentIndex = 0);
  }

  void _logout() async {
    _unreadTimer?.cancel();
    await ApiService.clearAuth();
    setState(() {
      _loggedIn = false;
      _profile = null;
      _currentIndex = 0;
      _unreadCount = 0;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (!_loggedIn) {
      return LoginScreen(
        onLoginSuccess: _onLoginSuccess,
        onGoToRegister: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => RegisterScreen(onRegisterSuccess: _onLoginSuccess),
            ),
          );
        },
      );
    }

    final screens = [
      const JobsScreen(),
      const ApplicationsScreen(),
      const TestsScreen(),
      const LiveCodingScreen(),
      const CalendarScreen(),
      const ReviewsScreen(),
      NotificationsScreen(onViewed: _fetchUnreadCount),
      ProfileScreen(onLogout: _logout),
    ];

    return Scaffold(
      body: screens[_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (i) {
          setState(() => _currentIndex = i);
          if (i == 6) _fetchUnreadCount();
        },
        destinations: [
          const NavigationDestination(icon: Icon(Icons.work_outline), selectedIcon: Icon(Icons.work), label: 'Вакансии'),
          const NavigationDestination(icon: Icon(Icons.send_outlined), selectedIcon: Icon(Icons.send), label: 'Заявки'),
          const NavigationDestination(icon: Icon(Icons.quiz_outlined), selectedIcon: Icon(Icons.quiz), label: 'Тесты'),
          const NavigationDestination(icon: Icon(Icons.code), selectedIcon: Icon(Icons.code), label: 'Live Code'),
          const NavigationDestination(icon: Icon(Icons.calendar_month_outlined), selectedIcon: Icon(Icons.calendar_month), label: 'Календарь'),
          const NavigationDestination(icon: Icon(Icons.rate_review_outlined), selectedIcon: Icon(Icons.rate_review), label: 'Отзывы'),
          NavigationDestination(
            icon: Badge(
              isLabelVisible: _unreadCount > 0,
              label: Text('$_unreadCount'),
              child: const Icon(Icons.notifications_none),
            ),
            selectedIcon: Badge(
              isLabelVisible: _unreadCount > 0,
              label: Text('$_unreadCount'),
              child: const Icon(Icons.notifications),
            ),
            label: 'Уведомления',
          ),
          const NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Профиль'),
        ],
      ),
    );
  }
}
