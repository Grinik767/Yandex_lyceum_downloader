import os
import sys
from auth import auth
from pickle import load
from main_config import my_user_agent
from pyquery import PyQuery
from funcs import get_clean_name, html_to_pdf
import zipfile
import io

if os.path.exists('auth.pkl'):
    file = open('auth.pkl', 'rb')
    session = load(file)
    try:
        PyQuery(session.get('https://lyceum.yandex.ru/', headers={'User-Agent': my_user_agent}).text)(
            'span.user-account__name:first').text()
    except Exception:
        print('Произошла ошибка. Попробуйте удалить файл "auth.pkl"')
        sys.exit(1)
else:
    auth()
    file = open('auth.pkl', 'rb')
    session = load(file)

courses = PyQuery(session.get('https://lyceum.yandex.ru/', headers={'User-Agent': my_user_agent}).text)(
    'ul.courses__list')
courses_names = courses.text().split('\n')
ready_courses = '\n'.join([f"{i + 1} - {courses_names[i]}" for i in range(len(courses_names))])
item = input(f'Выберите курс: \n{ready_courses})\n')
try:
    course_name = courses_names[int(item) - 1]
except Exception:
    print('Произошла ошибка.')
    sys.exit(1)
os.mkdir(get_clean_name(course_name))
course_link = PyQuery(courses)(f'a:Contains("{course_name}")').attr['href']
course_id = course_link.split('/')[-3]
group_id = course_link.split('/')[-1]
course = session.get(f'https://lyceum.yandex.ru{course_link}', headers={'User-Agent': my_user_agent}).text
themes = PyQuery(course)('a.link-list__link').items()
for theme in themes:
    os.mkdir(f"{get_clean_name(course_name)}/{get_clean_name(theme('h4.lesson-card__lesson-title').text())}")
    theme_link = PyQuery(theme).attr['href']
    theme_id = theme_link.split('/')[-1]
    lessons = session.get(
        f'https://lyceum.yandex.ru/api/student/lessonTasks?courseId={course_id}&lessonId={theme_id}', headers={
            'User-Agent': my_user_agent}).json()
    for lesson in lessons:
        tasks = lesson['tasks']
        try:
            theory_id = session.get(f'https://lyceum.yandex.ru/api/materials?lessonId={theme_id}', headers={
                'User-Agent': my_user_agent}).json()[0]['id']
            theory = session.get(
                f'https://lyceum.yandex.ru/api/student/materials/{theory_id}?groupId={group_id}&lessonId={theme_id}',
                headers={
                    'User-Agent': my_user_agent}).json()['detailedMaterial']['content']
            html_to_pdf(theory,
                        path=f"{get_clean_name(course_name)}/{get_clean_name(theme('h4.lesson-card__lesson-title').text())}/Теория.pdf")
        except Exception:
            pass
        for task in tasks:
            try:
                if task['solution']['score'] > 0:
                    sol_id = task['solution']['id']
                    task_name = task['title']
                    task_id = task['id']
                    task_item = session.get(
                        f'https://lyceum.yandex.ru/api/student/tasks/{task_id}?groupId={group_id}',
                        headers={
                            'User-Agent': my_user_agent}).json()
                    usl = task_item['description']
                    html_to_pdf(usl,
                                path=f"{get_clean_name(course_name)}/{get_clean_name(theme('h4.lesson-card__lesson-title').text())}/{get_clean_name(task_name)}-условие.pdf")
                    solution = task_item['latestSubmission']['file']['url']
                    if solution.endswith('.zip'):
                        r = session.get(solution)
                        z = zipfile.ZipFile(io.BytesIO(r.content))
                        os.mkdir(
                            f"{get_clean_name(course_name)}/{get_clean_name(theme('h4.lesson-card__lesson-title').text())}/{get_clean_name(task_name)}")
                        z.extractall(
                            f"{get_clean_name(course_name)}/{get_clean_name(theme('h4.lesson-card__lesson-title').text())}/{get_clean_name(task_name)}")
                    else:
                        r = session.get(solution, headers={'User-Agent': my_user_agent})
                        with open(
                                f"{get_clean_name(course_name)}/{get_clean_name(theme('h4.lesson-card__lesson-title').text())}/{get_clean_name(task_name)}.py",
                                'wb') as f:
                            f.write(r.content)
            except Exception:
                pass
