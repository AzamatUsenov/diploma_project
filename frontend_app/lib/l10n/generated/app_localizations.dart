import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_ru.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'generated/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[Locale('ru')];

  /// No description provided for @appTitle.
  ///
  /// In ru, this message translates to:
  /// **'JobPlatform'**
  String get appTitle;

  /// No description provided for @vacancies.
  ///
  /// In ru, this message translates to:
  /// **'Вакансии'**
  String get vacancies;

  /// No description provided for @applications.
  ///
  /// In ru, this message translates to:
  /// **'Заявки'**
  String get applications;

  /// No description provided for @tests.
  ///
  /// In ru, this message translates to:
  /// **'Тесты'**
  String get tests;

  /// No description provided for @notifications.
  ///
  /// In ru, this message translates to:
  /// **'Уведомления'**
  String get notifications;

  /// No description provided for @profile.
  ///
  /// In ru, this message translates to:
  /// **'Профиль'**
  String get profile;

  /// No description provided for @login.
  ///
  /// In ru, this message translates to:
  /// **'Войти'**
  String get login;

  /// No description provided for @register.
  ///
  /// In ru, this message translates to:
  /// **'Создать аккаунт'**
  String get register;

  /// No description provided for @logout.
  ///
  /// In ru, this message translates to:
  /// **'Выйти'**
  String get logout;

  /// No description provided for @logoutConfirm.
  ///
  /// In ru, this message translates to:
  /// **'Вы уверены, что хотите выйти из аккаунта?'**
  String get logoutConfirm;

  /// No description provided for @cancel.
  ///
  /// In ru, this message translates to:
  /// **'Отмена'**
  String get cancel;

  /// No description provided for @save.
  ///
  /// In ru, this message translates to:
  /// **'Сохранить'**
  String get save;

  /// No description provided for @apply.
  ///
  /// In ru, this message translates to:
  /// **'Применить'**
  String get apply;

  /// No description provided for @reset.
  ///
  /// In ru, this message translates to:
  /// **'Сбросить'**
  String get reset;

  /// No description provided for @search.
  ///
  /// In ru, this message translates to:
  /// **'Поиск вакансий...'**
  String get search;

  /// No description provided for @filters.
  ///
  /// In ru, this message translates to:
  /// **'Фильтры'**
  String get filters;

  /// No description provided for @salary.
  ///
  /// In ru, this message translates to:
  /// **'Зарплата'**
  String get salary;

  /// No description provided for @sorting.
  ///
  /// In ru, this message translates to:
  /// **'Сортировка'**
  String get sorting;

  /// No description provided for @conditions.
  ///
  /// In ru, this message translates to:
  /// **'Условия'**
  String get conditions;

  /// No description provided for @remoteWork.
  ///
  /// In ru, this message translates to:
  /// **'Удалённая работа'**
  String get remoteWork;

  /// No description provided for @trainingProvided.
  ///
  /// In ru, this message translates to:
  /// **'Обучение предоставляется'**
  String get trainingProvided;

  /// No description provided for @minHonesty.
  ///
  /// In ru, this message translates to:
  /// **'Минимальная честность'**
  String get minHonesty;

  /// No description provided for @newestFirst.
  ///
  /// In ru, this message translates to:
  /// **'Сначала новые'**
  String get newestFirst;

  /// No description provided for @bySalary.
  ///
  /// In ru, this message translates to:
  /// **'По зарплате (больше)'**
  String get bySalary;

  /// No description provided for @byHonesty.
  ///
  /// In ru, this message translates to:
  /// **'По честности (выше)'**
  String get byHonesty;

  /// No description provided for @byExperience.
  ///
  /// In ru, this message translates to:
  /// **'По опыту (меньше)'**
  String get byExperience;

  /// No description provided for @vacancyCount.
  ///
  /// In ru, this message translates to:
  /// **'{count} вакансий'**
  String vacancyCount(Object count);

  /// No description provided for @compareSelect.
  ///
  /// In ru, this message translates to:
  /// **'Выберите вакансии ({count}/4)'**
  String compareSelect(Object count);

  /// No description provided for @compare.
  ///
  /// In ru, this message translates to:
  /// **'Сравнить'**
  String get compare;

  /// No description provided for @compareInfo.
  ///
  /// In ru, this message translates to:
  /// **'Выберите от 2 до 4 вакансий для сравнения'**
  String get compareInfo;

  /// No description provided for @maxCompare.
  ///
  /// In ru, this message translates to:
  /// **'Максимум 4 вакансии для сравнения'**
  String get maxCompare;

  /// No description provided for @minCompare.
  ///
  /// In ru, this message translates to:
  /// **'Выберите минимум 2 вакансии'**
  String get minCompare;

  /// No description provided for @noVacancies.
  ///
  /// In ru, this message translates to:
  /// **'Вакансии не найдены'**
  String get noVacancies;

  /// No description provided for @tryChangeFilters.
  ///
  /// In ru, this message translates to:
  /// **'Попробуйте изменить фильтры'**
  String get tryChangeFilters;

  /// No description provided for @noApplications.
  ///
  /// In ru, this message translates to:
  /// **'Нет заявок'**
  String get noApplications;

  /// No description provided for @applicationsHint.
  ///
  /// In ru, this message translates to:
  /// **'Ваши отклики появятся здесь'**
  String get applicationsHint;

  /// No description provided for @noTests.
  ///
  /// In ru, this message translates to:
  /// **'Нет доступных тестов'**
  String get noTests;

  /// No description provided for @testsHint.
  ///
  /// In ru, this message translates to:
  /// **'Тесты появятся здесь'**
  String get testsHint;

  /// No description provided for @noNotifications.
  ///
  /// In ru, this message translates to:
  /// **'Нет уведомлений'**
  String get noNotifications;

  /// No description provided for @notificationsHint.
  ///
  /// In ru, this message translates to:
  /// **'Здесь появятся уведомления об откликах,\nсообщениях и результатах тестов'**
  String get notificationsHint;

  /// No description provided for @allRead.
  ///
  /// In ru, this message translates to:
  /// **'Все уведомления прочитаны'**
  String get allRead;

  /// No description provided for @readAll.
  ///
  /// In ru, this message translates to:
  /// **'Прочитать все'**
  String get readAll;

  /// No description provided for @accepted.
  ///
  /// In ru, this message translates to:
  /// **'Принято'**
  String get accepted;

  /// No description provided for @rejected.
  ///
  /// In ru, this message translates to:
  /// **'Отклонено'**
  String get rejected;

  /// No description provided for @reviewed.
  ///
  /// In ru, this message translates to:
  /// **'Просмотрено'**
  String get reviewed;

  /// No description provided for @pending.
  ///
  /// In ru, this message translates to:
  /// **'Ожидает'**
  String get pending;

  /// No description provided for @chat.
  ///
  /// In ru, this message translates to:
  /// **'Чат'**
  String get chat;

  /// No description provided for @reject.
  ///
  /// In ru, this message translates to:
  /// **'Отклонить'**
  String get reject;

  /// No description provided for @accept.
  ///
  /// In ru, this message translates to:
  /// **'Принять'**
  String get accept;

  /// No description provided for @updateError.
  ///
  /// In ru, this message translates to:
  /// **'Ошибка обновления'**
  String get updateError;

  /// No description provided for @hrStats.
  ///
  /// In ru, this message translates to:
  /// **'Статистика HR'**
  String get hrStats;

  /// No description provided for @skillTests.
  ///
  /// In ru, this message translates to:
  /// **'Тесты навыков'**
  String get skillTests;

  /// No description provided for @questions.
  ///
  /// In ru, this message translates to:
  /// **'{count} вопросов'**
  String questions(Object count);

  /// No description provided for @finishTest.
  ///
  /// In ru, this message translates to:
  /// **'Завершить тест'**
  String get finishTest;

  /// No description provided for @answerAll.
  ///
  /// In ru, this message translates to:
  /// **'Ответьте на все вопросы'**
  String get answerAll;

  /// No description provided for @submitError.
  ///
  /// In ru, this message translates to:
  /// **'Ошибка отправки'**
  String get submitError;

  /// No description provided for @excellentResult.
  ///
  /// In ru, this message translates to:
  /// **'Отличный результат!'**
  String get excellentResult;

  /// No description provided for @goodResult.
  ///
  /// In ru, this message translates to:
  /// **'Неплохо, но есть куда расти'**
  String get goodResult;

  /// No description provided for @needStudy.
  ///
  /// In ru, this message translates to:
  /// **'Стоит подучить материал'**
  String get needStudy;

  /// No description provided for @backToTests.
  ///
  /// In ru, this message translates to:
  /// **'Вернуться к тестам'**
  String get backToTests;

  /// No description provided for @correctOf.
  ///
  /// In ru, this message translates to:
  /// **'{score} из {total} правильных'**
  String correctOf(Object score, Object total);

  /// No description provided for @settings.
  ///
  /// In ru, this message translates to:
  /// **'Настройки'**
  String get settings;

  /// No description provided for @editProfile.
  ///
  /// In ru, this message translates to:
  /// **'Редактировать профиль'**
  String get editProfile;

  /// No description provided for @darkTheme.
  ///
  /// In ru, this message translates to:
  /// **'Тёмная тема'**
  String get darkTheme;

  /// No description provided for @phone.
  ///
  /// In ru, this message translates to:
  /// **'Телефон'**
  String get phone;

  /// No description provided for @aboutMe.
  ///
  /// In ru, this message translates to:
  /// **'О себе'**
  String get aboutMe;

  /// No description provided for @skills.
  ///
  /// In ru, this message translates to:
  /// **'Навыки'**
  String get skills;

  /// No description provided for @info.
  ///
  /// In ru, this message translates to:
  /// **'Информация'**
  String get info;

  /// No description provided for @profileUpdated.
  ///
  /// In ru, this message translates to:
  /// **'Профиль обновлён'**
  String get profileUpdated;

  /// No description provided for @saveError.
  ///
  /// In ru, this message translates to:
  /// **'Ошибка сохранения'**
  String get saveError;

  /// No description provided for @welcomeBack.
  ///
  /// In ru, this message translates to:
  /// **'С возвращением!'**
  String get welcomeBack;

  /// No description provided for @loginToApp.
  ///
  /// In ru, this message translates to:
  /// **'Войдите в JobPlatform'**
  String get loginToApp;

  /// No description provided for @username.
  ///
  /// In ru, this message translates to:
  /// **'Имя пользователя'**
  String get username;

  /// No description provided for @password.
  ///
  /// In ru, this message translates to:
  /// **'Пароль'**
  String get password;

  /// No description provided for @noAccount.
  ///
  /// In ru, this message translates to:
  /// **'Нет аккаунта? Зарегистрироваться'**
  String get noAccount;

  /// No description provided for @fillAllFields.
  ///
  /// In ru, this message translates to:
  /// **'Заполните все поля'**
  String get fillAllFields;

  /// No description provided for @connectionError.
  ///
  /// In ru, this message translates to:
  /// **'Ошибка подключения к серверу'**
  String get connectionError;

  /// No description provided for @createAccount.
  ///
  /// In ru, this message translates to:
  /// **'Создайте аккаунт'**
  String get createAccount;

  /// No description provided for @whoAreYou.
  ///
  /// In ru, this message translates to:
  /// **'Кто вы?'**
  String get whoAreYou;

  /// No description provided for @applicant.
  ///
  /// In ru, this message translates to:
  /// **'Соискатель'**
  String get applicant;

  /// No description provided for @hrManager.
  ///
  /// In ru, this message translates to:
  /// **'HR менеджер'**
  String get hrManager;

  /// No description provided for @yourLevel.
  ///
  /// In ru, this message translates to:
  /// **'Ваш уровень'**
  String get yourLevel;

  /// No description provided for @passwordMin.
  ///
  /// In ru, this message translates to:
  /// **'Пароль минимум 6 символов'**
  String get passwordMin;

  /// No description provided for @email.
  ///
  /// In ru, this message translates to:
  /// **'Email'**
  String get email;

  /// No description provided for @requirementsInflated.
  ///
  /// In ru, this message translates to:
  /// **'Требования завышены'**
  String get requirementsInflated;

  /// No description provided for @remote.
  ///
  /// In ru, this message translates to:
  /// **'Remote'**
  String get remote;

  /// No description provided for @training.
  ///
  /// In ru, this message translates to:
  /// **'Обучение'**
  String get training;

  /// No description provided for @yearsExperience.
  ///
  /// In ru, this message translates to:
  /// **'{years} лет опыта'**
  String yearsExperience(Object years);

  /// No description provided for @yearsShort.
  ///
  /// In ru, this message translates to:
  /// **'{years} лет'**
  String yearsShort(Object years);

  /// No description provided for @addedToFavorites.
  ///
  /// In ru, this message translates to:
  /// **'Добавлено в избранное!'**
  String get addedToFavorites;

  /// No description provided for @alreadyFavorite.
  ///
  /// In ru, this message translates to:
  /// **'Уже в избранном'**
  String get alreadyFavorite;

  /// No description provided for @favorites.
  ///
  /// In ru, this message translates to:
  /// **'Избранное'**
  String get favorites;

  /// No description provided for @applyToJob.
  ///
  /// In ru, this message translates to:
  /// **'Откликнуться'**
  String get applyToJob;

  /// No description provided for @coverLetter.
  ///
  /// In ru, this message translates to:
  /// **'Сопроводительное письмо'**
  String get coverLetter;

  /// No description provided for @coverLetterHint.
  ///
  /// In ru, this message translates to:
  /// **'Расскажите, почему вы подходите...'**
  String get coverLetterHint;

  /// No description provided for @coverLetterOptional.
  ///
  /// In ru, this message translates to:
  /// **'Необязательно, но повышает шансы'**
  String get coverLetterOptional;

  /// No description provided for @sendApplication.
  ///
  /// In ru, this message translates to:
  /// **'Отправить отклик'**
  String get sendApplication;

  /// No description provided for @applicationSent.
  ///
  /// In ru, this message translates to:
  /// **'Отклик отправлен!'**
  String get applicationSent;

  /// No description provided for @jobAnalysis.
  ///
  /// In ru, this message translates to:
  /// **'Анализ вакансии'**
  String get jobAnalysis;

  /// No description provided for @honesty.
  ///
  /// In ru, this message translates to:
  /// **'Честность'**
  String get honesty;

  /// No description provided for @realLevel.
  ///
  /// In ru, this message translates to:
  /// **'Реальный уровень'**
  String get realLevel;

  /// No description provided for @skillsCount.
  ///
  /// In ru, this message translates to:
  /// **'Навыков'**
  String get skillsCount;

  /// No description provided for @adequate.
  ///
  /// In ru, this message translates to:
  /// **'Адекватные'**
  String get adequate;

  /// No description provided for @inflated.
  ///
  /// In ru, this message translates to:
  /// **'Завышены'**
  String get inflated;

  /// No description provided for @yourMatch.
  ///
  /// In ru, this message translates to:
  /// **'Ваш матч'**
  String get yourMatch;

  /// No description provided for @recommendApply.
  ///
  /// In ru, this message translates to:
  /// **'Рекомендуем подавать'**
  String get recommendApply;

  /// No description provided for @shouldImprove.
  ///
  /// In ru, this message translates to:
  /// **'Стоит подтянуть навыки'**
  String get shouldImprove;

  /// No description provided for @matchingSkills.
  ///
  /// In ru, this message translates to:
  /// **'Совпадающие ({count})'**
  String matchingSkills(Object count);

  /// No description provided for @missingSkills.
  ///
  /// In ru, this message translates to:
  /// **'Нужно изучить ({count})'**
  String missingSkills(Object count);

  /// No description provided for @learningPlan.
  ///
  /// In ru, this message translates to:
  /// **'План обучения'**
  String get learningPlan;

  /// No description provided for @description.
  ///
  /// In ru, this message translates to:
  /// **'Описание'**
  String get description;

  /// No description provided for @requirements.
  ///
  /// In ru, this message translates to:
  /// **'Требования'**
  String get requirements;

  /// No description provided for @onboardingTitle1.
  ///
  /// In ru, this message translates to:
  /// **'Честные вакансии'**
  String get onboardingTitle1;

  /// No description provided for @onboardingText1.
  ///
  /// In ru, this message translates to:
  /// **'Мы анализируем требования и показываем реальный уровень каждой вакансии. Никаких \"Junior с 5-летним опытом\".'**
  String get onboardingText1;

  /// No description provided for @onboardingTitle2.
  ///
  /// In ru, this message translates to:
  /// **'Умный матчинг'**
  String get onboardingTitle2;

  /// No description provided for @onboardingText2.
  ///
  /// In ru, this message translates to:
  /// **'Платформа сравнивает ваши навыки с требованиями и подсказывает, куда стоит откликнуться и что подтянуть.'**
  String get onboardingText2;

  /// No description provided for @onboardingTitle3.
  ///
  /// In ru, this message translates to:
  /// **'Тесты навыков'**
  String get onboardingTitle3;

  /// No description provided for @onboardingText3.
  ///
  /// In ru, this message translates to:
  /// **'Проходите тесты, подтверждайте свой уровень и повышайте шансы получить работу мечты.'**
  String get onboardingText3;

  /// No description provided for @skip.
  ///
  /// In ru, this message translates to:
  /// **'Пропустить'**
  String get skip;

  /// No description provided for @next.
  ///
  /// In ru, this message translates to:
  /// **'Далее'**
  String get next;

  /// No description provided for @start.
  ///
  /// In ru, this message translates to:
  /// **'Начать'**
  String get start;

  /// No description provided for @salaryNotSpecified.
  ///
  /// In ru, this message translates to:
  /// **'Не указана'**
  String get salaryNotSpecified;

  /// No description provided for @loadError.
  ///
  /// In ru, this message translates to:
  /// **'Ошибка загрузки'**
  String get loadError;

  /// No description provided for @couldNotLoadProfile.
  ///
  /// In ru, this message translates to:
  /// **'Не удалось загрузить профиль'**
  String get couldNotLoadProfile;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['ru'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'ru':
      return AppLocalizationsRu();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
