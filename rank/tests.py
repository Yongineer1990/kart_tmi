import json
import jwt

from django.test import (
    TestCase,
    Client,
)
from unittest.mock import (
    patch,
    MagicMock,
)

from .models import (
    GameUser,
    Comment,
    Detail,
    UserPageHit,
    Ranking,
    TeamType
)
from user.models import Users
from config.settings import (
    SECRET_KEY,
    ALGORITHM,
)

class CommentTest(TestCase):
    def setUp(self):
        GameUser.objects.create(
            id          = 100,
            access_id   = 'test1',
            nickname    = 'from_user'
        )
        GameUser.objects.create(
            id          = 101,
            access_id   = 'test2',
            nickname    = 'to_user'
        )
        Users.objects.create(
            email           = 'unittest@google.com',
            picture         = 'naver.com',
            game_user_id    = GameUser.objects.get(access_id='test1').id
        )

    def tearDown(self):
        GameUser.objects.filter(access_id='test1').delete()
        GameUser.objects.filter(access_id='test2').delete()
        Users.objects.filter(email = 'unittest@google.com').delete()
        Comment.objects.filter(comment='test').delete()

    def test_post_comment_pass(self):
        client = Client()

        user_email  = Users.objects.get(email='unittest@google.com').email
        token       = jwt.encode({'email' : user_email}, SECRET_KEY, algorithm=ALGORITHM)
        token       = token.decode('utf-8')

        to_user     = GameUser.objects.get(access_id='test2').access_id

        testsuit    = {"comment" : "test"}
        headers     = {
            'HTTP_Authorization' : token,
            'content_type' : 'application/json'
        }
        response    = client.post(f'/rank/comment/{to_user}', json.dumps(testsuit), **headers)

        self.assertEqual(response.status_code, 200)

    def test_post_comment_fail(self):
        client  = Client()
        to_user = GameUser.objects.get(access_id='test2').access_id

        testsuit    = {"comment" : "test"}
        headers     = {
            'HTTP_Authorization' : '',
            'content_type' : 'application/json'
        }
        response    = client.post(f'/rank/comment/{to_user}', json.dumps(testsuit), **headers)
        self.assertEqual(response.status_code, 401)

    def test_get_comment_pass(self):
        client  = Client()
        to_user = GameUser.objects.get(access_id='test2').access_id
        comment = Comment.objects.filter(to_id=to_user).values()

        headers     = {
            'content_type' : 'application/json'
        }
        response    = client.get(f'/rank/comment/{to_user}', **headers)

        self.assertEqual(response.json(), {'comment' : list(comment)})
        self.assertEqual(response.status_code, 200)

    def test_get_comment_fail(self):
        client  = Client()
        headers = {
            'content_type' : 'application/json'
        }
        response = client.get(f'/rank/comment/wrong_id', **headers)

        self.assertEqual(response.status_code, 400)

class RankDetailTest(TestCase):
    def test_get_detail_pass(self):
        client = Client()
        access_id = GameUser.objects.get(id=1).access_id
        headers = {
            'content_type' : 'application/json'
        }
        response = client.get(f'/rank/detail/{access_id}',**headers)

        self.assertEqual(response.status_code, 200)

    def test_get_detail_fail(self):
        client = Client()
        access_id = 'Wrong ID'
        headers = {
            'content_type' : 'application/json'
        }
        response = client.get(f'/rank/detail/{access_id}',**headers)

        self.assertEqual(response.status_code, 400)

class IndiRankTest(TestCase):

    def setUp(self):

        TeamType.objects.create(
            name = "개인전"
        )

        GameUser.objects.create(
            id        = 1,
            access_id = 'test1',
            nickname  = 'from_user',
            team_id   = 1,
            rank      = 23
        )
        Ranking.objects.create(
            rank         = 33,
            cumul_point  = 125,
            point_get    = 23,
            win_pct      = 0.62,
            retire_pct   = 0.01,
            play_cnt     = 55, 
            game_user_id = GameUser.objects.get(access_id='test1').id,
            team_type_id = TeamType.objects.get(id=1).id
        )

    def tearDown(self):
        GameUser.objects.all().delete()
        TeamType.objects.all().delete()
        Ranking.objects.all().delete()
    
    def test_indi_rank_list_pass(self):
        client  = Client()

        response = client.get('/rank/indiranklist', content_type='applications/json')
        
        test_dict = {
            'indi_rank_list': 
                [
                    {
                        'id'           : 1, 
                        'rank'         : 33, 
                        'rank_diff'    : None, 
                        'cumul_point'  : 125, 
                        'point_get'    : 23, 
                        'win_pct'      : '0.62', 
                        'retire_pct'   : '0.01', 
                        'play_cnt'     : 55, 
                        'avg_rank'     : None, 
                        'game_user_id' : 1, 
                        'team_type_id' : 1, 
                        'nickname'     : 'from_user',
                        'access_id'    : 'test1',
                        'matchType'    : '7b9f0fd5377c38514dbb78ebe63ac6c3b81009d5a31dd569d1cff8f005aa881a'
                    }
                ]
            }       
        
        self.assertEqual(response.json(), test_dict)
        self.assertEqual(response.status_code, 200)
    
class TeamRankTest(TestCase):

    def setUp(self):
        
        TeamType.objects.create(
            name = "팀전"
        )

        GameUser.objects.create(
            id        = 1,
            access_id = 'test2',
            nickname  = 'to_user',
            team_id   = 2,
            rank      = 23
        )

        Ranking.objects.create(
            rank         = 23,
            cumul_point  = 125,
            point_get    = 23,
            win_pct      = 0.62,
            retire_pct   = 0.01,
            play_cnt     = 55, 
            game_user_id = GameUser.objects.get(access_id='test2').id,
            team_type_id = TeamType.objects.get(id=2).id
        )

    def tearDown(self):
        GameUser.objects.all().delete()
        TeamType.objects.all().delete()
        Ranking.objects.all().delete()
    
    def test_team_rank_list_pass(self):
        client  = Client()

        response = client.get('/rank/teamranklist', content_type='applications/json')

        test_dict = {
            'team_rank_list': 
                [
                    {
                        'id'           : 2, 
                        'rank'         : 23, 
                        'rank_diff'    : None, 
                        'cumul_point'  : 125, 
                        'point_get'    : 23, 
                        'win_pct'      : '0.62', 
                        'retire_pct'   : '0.01', 
                        'play_cnt'     : 55, 
                        'avg_rank'     : None, 
                        'game_user_id' : 1, 
                        'team_type_id' : 2, 
                        'nickname'     : 'to_user',
                        'access_id'    : 'test2',
                        'matchType'    : 'effd66758144a29868663aa50e85d3d95c5bc0147d7fdb9802691c2087f3416e'
                    }
                ]
            }       

        self.assertEqual(response.json(), test_dict)
        self.assertEqual(response.status_code, 200)
