// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Russian (`ru`).
class AppLocalizationsRu extends AppLocalizations {
  AppLocalizationsRu([String locale = 'ru']) : super(locale);

  @override
  String get appTitle => 'JobPlatform';

  @override
  String get vacancies => 'Вакансии';

  @override
  String get applications => 'Заявки';

  @override
  String get tests => 'Тесты';

  @override
  String get notifications => 'Уведомления';

  @override
  String get profile => 'Профиль';

  @override
  String get login => 'Войти';

  @override
  String get register => 'Создать аккаунт';

  @override
  String get logout => 'Выйти';

  @override
  String get logoutConfirm => 'Вы уверены, что хотите выйти из аккаунта?';

  @override
  String get cancel => 'Отмена';

  @override
  String get save => 'Сохранить';

  @override
  String get apply => 'Применить';

  @override
  String get reset => 'Сбросить';

  @override
  String get search => 'Поиск вакансий...';

  @override
  String get filters => 'Фильтры';

  @override
  String get salary => 'Зарплата';

  @override
  String get sorting => 'Сортировка';

  @override
  String get conditions => 'Условия';

  @override
  String get remoteWork => 'Удалённая работа';

  @override
  String get trainingProvided => 'Обучение предоставляется';

  @override
  String get minHonesty => 'Минимальная честность';

  @override
  String get newestFirst => 'Сначала новые';

  @override
  String get bySalary => 'По зарплате (больше)';

  @override
  String get byHonesty => 'По честности (выше)';

  @override
  String get byExperience => 'По опыту (меньше)';

  @override
  String vacancyCount(Object count) {
    return '$count вакансий';
  }

  @override
  String compareSelect(Object count) {
    return 'Выберите вакансии ($count/4)';
  }

  @override
  String get compare => 'Сравнить';

  @override
  String get compareInfo => 'Выберите от 2 до 4 вакансий для сравнения';

  @override
  String get maxCompare => 'Максимум 4 вакансии для сравнения';

  @override
  String get minCompare => 'Выберите минимум 2 вакансии';

  @override
  String get noVacancies => 'Вакансии не найдены';

  @override
  String get tryChangeFilters => 'Попробуйте изменить фильтры';

  @override
  String get noApplications => 'Нет заявок';

  @override
  String get applicationsHint => 'Ваши отклики появятся здесь';

  @override
  String get noTests => 'Нет доступных тестов';

  @override
  String get testsHint => 'Тесты появятся здесь';

  @override
  String get noNotifications => 'Нет уведомлений';

  @override
  String get notificationsHint =>
      'Здесь появятся уведомления об откликах,\nсообщениях и результатах тестов';

  @override
  String get allRead => 'Все уведомления прочитаны';

  @override
  String get readAll => 'Прочитать все';

  @override
  String get accepted => 'Принято';

  @override
  String get rejected => 'Отклонено';

  @override
  String get reviewed => 'Просмотрено';

  @override
  String get pending => 'Ожидает';

  @override
  String get chat => 'Чат';

  @override
  String get reject => 'Отклонить';

  @override
  String get accept => 'Принять';

  @override
  String get updateError => 'Ошибка обновления';

  @override
  String get hrStats => 'Статистика HR';

  @override
  String get skillTests => 'Тесты навыков';

  @override
  String questions(Object count) {
    return '$count вопросов';
  }

  @override
  String get finishTest => 'Завершить тест';

  @override
  String get answerAll => 'Ответьте на все вопросы';

  @override
  String get submitError => 'Ошибка отправки';

  @override
  String get excellentResult => 'Отличный результат!';

  @override
  String get goodResult => 'Неплохо, но есть куда расти';

  @override
  String get needStudy => 'Стоит подучить материал';

  @override
  String get backToTests => 'Вернуться к тестам';

  @override
  String correctOf(Object score, Object total) {
    return '$score из $total правильных';
  }

  @override
  String get settings => 'Настройки';

  @override
  String get editProfile => 'Редактировать профиль';

  @override
  String get darkTheme => 'Тёмная тема';

  @override
  String get phone => 'Телефон';

  @override
  String get aboutMe => 'О себе';

  @override
  String get skills => 'Навыки';

  @override
  String get info => 'Информация';

  @override
  String get profileUpdated => 'Профиль обновлён';

  @override
  String get saveError => 'Ошибка сохранения';

  @override
  String get welcomeBack => 'С возвращением!';

  @override
  String get loginToApp => 'Войдите в JobPlatform';

  @override
  String get username => 'Имя пользователя';

  @override
  String get password => 'Пароль';

  @override
  String get noAccount => 'Нет аккаунта? Зарегистрироваться';

  @override
  String get fillAllFields => 'Заполните все поля';

  @override
  String get connectionError => 'Ошибка подключения к серверу';

  @override
  String get createAccount => 'Создайте аккаунт';

  @override
  String get whoAreYou => 'Кто вы?';

  @override
  String get applicant => 'Соискатель';

  @override
  String get hrManager => 'HR менеджер';

  @override
  String get yourLevel => 'Ваш уровень';

  @override
  String get passwordMin => 'Пароль минимум 6 символов';

  @override
  String get email => 'Email';

  @override
  String get requirementsInflated => 'Требования завышены';

  @override
  String get remote => 'Remote';

  @override
  String get training => 'Обучение';

  @override
  String yearsExperience(Object years) {
    return '$years лет опыта';
  }

  @override
  String yearsShort(Object years) {
    return '$years лет';
  }

  @override
  String get addedToFavorites => 'Добавлено в избранное!';

  @override
  String get alreadyFavorite => 'Уже в избранном';

  @override
  String get favorites => 'Избранное';

  @override
  String get applyToJob => 'Откликнуться';

  @override
  String get coverLetter => 'Сопроводительное письмо';

  @override
  String get coverLetterHint => 'Расскажите, почему вы подходите...';

  @override
  String get coverLetterOptional => 'Необязательно, но повышает шансы';

  @override
  String get sendApplication => 'Отправить отклик';

  @override
  String get applicationSent => 'Отклик отправлен!';

  @override
  String get jobAnalysis => 'Анализ вакансии';

  @override
  String get honesty => 'Честность';

  @override
  String get realLevel => 'Реальный уровень';

  @override
  String get skillsCount => 'Навыков';

  @override
  String get adequate => 'Адекватные';

  @override
  String get inflated => 'Завышены';

  @override
  String get yourMatch => 'Ваш матч';

  @override
  String get recommendApply => 'Рекомендуем подавать';

  @override
  String get shouldImprove => 'Стоит подтянуть навыки';

  @override
  String matchingSkills(Object count) {
    return 'Совпадающие ($count)';
  }

  @override
  String missingSkills(Object count) {
    return 'Нужно изучить ($count)';
  }

  @override
  String get learningPlan => 'План обучения';

  @override
  String get description => 'Описание';

  @override
  String get requirements => 'Требования';

  @override
  String get onboardingTitle1 => 'Честные вакансии';

  @override
  String get onboardingText1 =>
      'Мы анализируем требования и показываем реальный уровень каждой вакансии. Никаких \"Junior с 5-летним опытом\".';

  @override
  String get onboardingTitle2 => 'Умный матчинг';

  @override
  String get onboardingText2 =>
      'Платформа сравнивает ваши навыки с требованиями и подсказывает, куда стоит откликнуться и что подтянуть.';

  @override
  String get onboardingTitle3 => 'Тесты навыков';

  @override
  String get onboardingText3 =>
      'Проходите тесты, подтверждайте свой уровень и повышайте шансы получить работу мечты.';

  @override
  String get skip => 'Пропустить';

  @override
  String get next => 'Далее';

  @override
  String get start => 'Начать';

  @override
  String get salaryNotSpecified => 'Не указана';

  @override
  String get loadError => 'Ошибка загрузки';

  @override
  String get couldNotLoadProfile => 'Не удалось загрузить профиль';
}
