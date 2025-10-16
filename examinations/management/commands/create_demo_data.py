from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from examinations.models import Category, Test
from questions.models import Question, Choice

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample tests and questions for demo'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')
        
        # Create teacher user if not exists
        teacher, created = User.objects.get_or_create(
            username='teacher1',
            defaults={
                'email': 'teacher@buxorotest.uz',
                'first_name': 'Ustoz',
                'last_name': 'Matematika',
                'role': 'teacher',
                'is_active': True
            }
        )
        if created:
            teacher.set_password('teacher123')
            teacher.save()
            self.stdout.write(f'Created teacher: {teacher.username}')

        # Create categories
        categories_data = [
            {'name': 'Matematika', 'description': 'Matematika fanidan testlar', 'icon': 'fa-calculator', 'color': '#007bff'},
            {'name': 'Fizika', 'description': 'Fizika fanidan testlar', 'icon': 'fa-atom', 'color': '#28a745'},
            {'name': 'Kimyo', 'description': 'Kimyo fanidan testlar', 'icon': 'fa-flask', 'color': '#dc3545'},
            {'name': 'Biologiya', 'description': 'Biologiya fanidan testlar', 'icon': 'fa-leaf', 'color': '#17a2b8'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create tests
        math_category = Category.objects.get(name='Matematika')
        physics_category = Category.objects.get(name='Fizika')
        
        tests_data = [
            {
                'title': 'Algebra asoslari',
                'description': 'Algebra bo\'yicha asosiy tushunchalar va amallar',
                'category': math_category,
                'difficulty': 'easy',
                'time_limit': 30,
                'pass_mark': 60,
                'status': 'published'
            },
            {
                'title': 'Geometriya asoslari', 
                'description': 'Geometrik shakllar va ularning xossalari',
                'category': math_category,
                'difficulty': 'medium',
                'time_limit': 45,
                'pass_mark': 70,
                'status': 'published'
            },
            {
                'title': 'Mexanika asoslari',
                'description': 'Fizikada mexanika qonunlari',
                'category': physics_category,
                'difficulty': 'medium',
                'time_limit': 40,
                'pass_mark': 65,
                'status': 'published'
            }
        ]
        
        for test_data in tests_data:
            test, created = Test.objects.get_or_create(
                title=test_data['title'],
                defaults={**test_data, 'created_by': teacher}
            )
            if created:
                self.stdout.write(f'Created test: {test.title}')
                
                # Create questions for each test
                if test.title == 'Algebra asoslari':
                    questions_data = [
                        {
                            'text': '2 + 2 = ?',
                            'choices': [('2', False), ('3', False), ('4', True), ('5', False)]
                        },
                        {
                            'text': '5 * 3 = ?',
                            'choices': [('15', True), ('12', False), ('18', False), ('20', False)]
                        },
                        {
                            'text': '10 - 7 = ?',
                            'choices': [('2', False), ('3', True), ('4', False), ('5', False)]
                        },
                        {
                            'text': '12 / 4 = ?',
                            'choices': [('2', False), ('3', True), ('4', False), ('6', False)]
                        },
                        {
                            'text': 'x + 5 = 10 tenglamada x ning qiymati nechaga teng?',
                            'choices': [('3', False), ('5', True), ('10', False), ('15', False)]
                        }
                    ]
                elif test.title == 'Geometriya asoslari':
                    questions_data = [
                        {
                            'text': 'To\'g\'ri burchak necha gradusga teng?',
                            'choices': [('45°', False), ('60°', False), ('90°', True), ('180°', False)]
                        },
                        {
                            'text': 'Uchburchakning ichki burchaklari yig\'indisi nechaga teng?',
                            'choices': [('90°', False), ('180°', True), ('270°', False), ('360°', False)]
                        },
                        {
                            'text': 'Kvadratning barcha tomonlari...',
                            'choices': [('Har xil', False), ('Teng', True), ('Parallel', False), ('Perpendikulyar', False)]
                        }
                    ]
                elif test.title == 'Mexanika asoslari':
                    questions_data = [
                        {
                            'text': 'Nyutonning birinchi qonuni nima?',
                            'choices': [('Inersiya qonuni', True), ('Kuch qonuni', False), ('Ta\'sir-qarshi ta\'sir qonuni', False), ('Tortishish qonuni', False)]
                        },
                        {
                            'text': 'Tezlik formulasi qaysi?',
                            'choices': [('v = s/t', True), ('v = s*t', False), ('v = s+t', False), ('v = s-t', False)]
                        }
                    ]
                
                for i, q_data in enumerate(questions_data):
                    question = Question.objects.create(
                        test=test,
                        text=q_data['text'],
                        question_type='single_choice',
                        points=1,
                        order=i+1,
                        created_by=teacher
                    )
                    
                    for choice_text, is_correct in q_data['choices']:
                        Choice.objects.create(
                            question=question,
                            text=choice_text,
                            is_correct=is_correct
                        )
                    
                    self.stdout.write(f'  Created question: {question.text[:50]}...')

        self.stdout.write(self.style.SUCCESS('Demo data created successfully!'))
