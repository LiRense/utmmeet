# Parameterized test with a full set of decorators
from os.path import join, dirname

import pytest
import testit


@testit.workItemIds(627)
@testit.displayName('Simple autotest 1 - {name}')
@testit.externalId('Simple_autotest1_{name}')
@testit.title('Authorization')
@testit.description('E2E_autotest')
@testit.labels('{labels}')
@testit.links(links=[
    {'url': '{url}', 'type': '{link_type}', 'title': '{link_title}', 'description': '{link_desc}'},
    {'url': '{url}', 'type': '{link_type}', 'title': '{link_title}', 'description': '{link_desc}'}
])
@pytest.mark.parametrize('name, labels, url, link_type, link_title, link_desc', [
    ('param 1', ['E2E', 'test'], 'https://dumps.example.com/module/JCP-777', testit.LinkType.DEFECT, 'JCP-777',
     'Desc of JCP-777'),
    ('param 2', (), 'https://dumps.example.com/module/docs', testit.LinkType.RELATED, 'Documentation',
     'Desc of JCP-777'),
    ('param 3', ('E2E', 'test'), 'https://dumps.example.com/module/projects', testit.LinkType.REQUIREMENT, 'Projects',
     'Desc of Projects'),
    ('param 4', {'E2E', 'test'}, 'https://dumps.example.com/module/', testit.LinkType.BLOCKED_BY, '', ''),
    ('param 5', 'test', 'https://dumps.example.com/module/repository', testit.LinkType.REPOSITORY, 'Repository',
     'Desc of Repository')
])
def test_1(name, labels, url, link_type, link_title, link_desc):
    testit.addLinks(url='https://dumps.example.com/module/some_module_dump', title='component_dump.dmp',
                    type=testit.LinkType.RELATED, description='Description')
    testit.addLinks(url='https://dumps.example.com/module/some_module_dump')
    testit.addLinks(links=[
        {'url': 'https://dumps.example.com/module/some_module_dump', 'type': testit.LinkType.BLOCKED_BY,
         'title': 'component_dump.dmp', 'description': 'Description'},
        {'url': 'https://dumps.example.com/module/some_module_dump', 'type': testit.LinkType.DEFECT},
        {'url': 'https://dumps.example.com/module/some_module_dump', 'type': testit.LinkType.ISSUE,
         'title': 'component_dump.dmp'},
        {'url': 'https://dumps.example.com/module/some_module_dump', 'type': testit.LinkType.REQUIREMENT,
         'title': 'component_dump.dmp', 'description': 'Description'},
        {'url': 'https://dumps.example.com/module/some_module_dump', 'type': testit.LinkType.REPOSITORY,
         'description': 'Description'},
        {'url': 'https://dumps.example.com/module/some_module_dump'}
    ])
    with testit.step('Log in the system', 'system authentication'):
        with testit.step('Enter the login', 'login was entered'):
            with testit.step('Enter the password', 'password was entered'):
                assert True
        with testit.step('Create a project', 'the project was created'):
            with testit.step('Enter the project', 'the contents of the project are displayed'):
                assert True
            with testit.step('Create a test case', 'test case was created'):
                assert True
    with testit.step('Attachments'):
        testit.addAttachments(
            join(dirname(__file__), 'docs/text_file.txt'),
            join(dirname(__file__), 'pictures/picture.jpg'),
            join(dirname(__file__), 'docs/document.docx')
        )
        testit.addAttachments(
            join(dirname(__file__), 'docs/document.doc'),
            join(dirname(__file__), 'docs/logs.log')
        )
        assert True