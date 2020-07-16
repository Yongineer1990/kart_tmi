import json

from django.views import View
from django.http import (
    JsonResponse,
    HttpResponse
)

from .models import (
    GameUser,
    Comment,
    Detail,
    UserPageHit
)
from user.utils import login_decorator

class CommentView(View):
    def get(self, request, user_id):
        try:
            if GameUser.objects.filter(access_id=user_id).exists():
                user     = GameUser.objects.get(access_id=user_id)
                comments = Comment.objects.filter(to_id=user).values()

                return JsonResponse({'comment' : list(comments)}, status=200)

            return JsonResponse({'Message' : 'INVALID_USER'}, status=400)

        except KeyError:
            return JsonResponse({'Message' : 'INVALID_KEYS'}, status=400)

    @login_decorator
    def post(self, request, user_id):
        try:
            data        = json.loads(request.body)
            from_user   = request.userinfo.game_user
            to_user     = GameUser.objects.get(access_id=user_id)

            Comment(
                comment = data['comment'],
                from_id = from_user,
                to_id   = to_user
            ).save()

            return HttpResponse(status=200)

        except KeyError:
            return JsonResponse({'Message' : 'INVALID_KEYS'}, status=400)

class RankDetailView(View):
    def get(self, request, access_id):
        try:
            gameuser = GameUser.objects.get(access_id=access_id)
            if UserPageHit.objects.filter(game_user=gameuser).exists():
                countview           = UserPageHit.objects.get(game_user=gameuser)
                countview.count     += 1
                countview.save()
            else:
                UserPageHit.objects.create(
                    count=1,
                    game_user=gameuser
                )

            gameuser = GameUser.objects.select_related('userpagehit', 'detail').get(access_id=access_id)
            detail      = gameuser.detail
            pageview    = gameuser.userpagehit

            win_ratio   = round(detail.win_cnt / detail.play_cnt, 2)

            return JsonResponse({
                'character' : {
                    'id'    : detail.character.id,
                    'name'  : detail.character.name,
                    'key'   : detail.character.key,
                    'img'   : detail.character.url
                },
                'pageview'      : pageview.count,
                'win_ratio'     : win_ratio,
                'retire_ratio'  : float(detail.retire_pct),
                'rank_avg_500'  : float(detail.rank_avg_500),
                'rank_avg_50'   : float(detail.rank_avg_50),
                'rank_list_50'  : eval(detail.rank_list_50)
            }, status=200)

        except KeyError:
            return JsonResponse({'Message' : 'INVALID_KEYS'}, status=400)

        except GameUser.DoesNotExist:
            return HttpResponse(status=400)
