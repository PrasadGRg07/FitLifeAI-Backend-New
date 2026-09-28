from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import UserProfile, Category, Product, Cart, CartItem, HealthScore
from .serializers import UserProfileSerializer, CategorySerializer, ProductSerializer, CartItemSerializer, CartSerializer


@api_view(['GET'])
def get_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)
@api_view(['GET'])
def get_product(request, pk): 
    try:
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(status=404)

    
    
@api_view(['GET'])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True, context={'request': request})
    return Response(serializer.data)
@api_view(['GET'])
def get_user_profiles(request):
    user_profiles = UserProfile.objects.all()
    serializer = UserProfileSerializer(user_profiles, many=True, context={'request': request})
    return Response(serializer.data)



@api_view(['GET'])
def get_cart(request):
    cart, created = Cart.objects.get_or_create(user=None)
    serializer= CartSerializer(cart)
    return Response(serializer.data)



@api_view(['POST'])
def add_to_cart(request):
    product_id = request.data.get('product_id')
    product = Product.objects.get(id=product_id)
    try:
        quantity = int(request.data.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    cart, created = Cart.objects.get_or_create(user=None)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        # increment existing item by requested quantity
        item.quantity += quantity
    else:
        # set quantity for newly created item
        item.quantity = quantity
    item.save()
    # return the full cart so frontend can sync
    return Response({'message': 'Product added to cart', "cart": CartSerializer(cart).data})

@api_view(['POST'])
def update_cart_quantity(request):  
    item_id = request.data.get('item_id')
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')
    
    if (not item_id and not product_id) or quantity is None:
        return Response({'error': 'Item ID or product ID and quantity are required'}, status=400)

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response({'error': 'Quantity must be an integer'}, status=400)

    try:
        if item_id:
            item = CartItem.objects.get(id=item_id)
        else:
            # find by product within the current cart
            cart, _ = Cart.objects.get_or_create(user=None)
            item = CartItem.objects.get(cart=cart, product__id=product_id)

        if quantity < 1:
            cart = item.cart
            item.delete()
            return Response({'message': 'Item removed', 'cart': CartSerializer(cart).data})

        item.quantity = quantity
        item.save()
        cart = item.cart
        return Response({'message': 'Quantity updated', 'cart': CartSerializer(cart).data})

    except CartItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=404)
    
    
      
      


@api_view(['POST'])
def remove_from_cart(request):
    item_id = request.data.get('item_id')
    CartItem.objects.get(id=item_id).delete()
    
    return Response({'message': 'Product removed from cart'})


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        data = serializer.data
        data['is_banned'] = profile.is_banned
        return Response(data)
    
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_score(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    score = request.data.get('weekly_score')
    if score is not None:
        score_val = int(round(float(score)))
        profile.weekly_score = score_val
        profile.save()
        # Save to history for accurate monthly analytics
        HealthScore.objects.create(user=request.user, score=score_val)
        return Response({'weekly_score': profile.weekly_score})
    return Response({'error': 'weekly_score required'}, status=400)


@api_view(['GET'])
def leaderboard(request):
    from django.utils import timezone
    from django.db.models import Avg, Max, Count
    from datetime import timedelta

    mode = request.query_params.get('mode', 'average')  # average | best | streak
    since = (timezone.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)

    scores_qs = (
        HealthScore.objects
        .filter(created_at__gte=since)
        .values('user_id')
        .annotate(avg=Avg('score'), best=Max('score'), days=Count('created_at__date', distinct=True))
    )

    if mode == 'best':
        scores_qs = scores_qs.order_by('-best')
    elif mode == 'streak':
        scores_qs = scores_qs.order_by('-days', '-avg')
    else:
        scores_qs = scores_qs.order_by('-avg')

    scores_qs = scores_qs[:10]

    user_ids = [s['user_id'] for s in scores_qs]
    profiles_map = {
        p.user_id: p
        for p in UserProfile.objects.filter(user_id__in=user_ids).select_related('user')
    }

    data = []
    for s in scores_qs:
        profile = profiles_map.get(s['user_id'])
        if not profile:
            continue
        if mode == 'best':
            display_score = round(s['best'], 1)
        elif mode == 'streak':
            display_score = round(s['avg'] * s['days'], 1)
        else:
            display_score = round(s['avg'], 1)
        data.append({
            'id': profile.user.id,
            'name': profile.name or profile.user.username,
            'score': display_score,
            'days_active': s['days'],
        })
    return Response(data)


# ── Admin endpoints ────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_analytics(request):
    from django.db.models.functions import TruncMonth
    from django.db.models import Count, Avg

    monthly_users = (
        User.objects.filter(is_superuser=False)
        .annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    monthly_active = (
        User.objects.filter(is_superuser=False, is_active=True)
        .annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Group health scores by actual prediction date
    monthly_scores = (
        HealthScore.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(avg_score=Avg('score'), count=Count('id'))
        .order_by('month')
    )

    active_map = {m['month'].strftime('%b %Y'): m['count'] for m in monthly_active}
    scores_map = {m['month'].strftime('%b %Y'): round(m['avg_score'], 1) for m in monthly_scores}

    data = [
        {
            'month': m['month'].strftime('%b %Y'),
            '_month': m['month'],
            'users': m['count'],
            'active': active_map.get(m['month'].strftime('%b %Y'), 0),
            'scores': scores_map.get(m['month'].strftime('%b %Y'), 0),
        }
        for m in monthly_users
    ]

    existing_months = {d['month'] for d in data}
    for s in monthly_scores:
        label = s['month'].strftime('%b %Y')
        if label not in existing_months:
            data.append({'month': label, '_month': s['month'], 'users': 0, 'active': 0, 'scores': round(s['avg_score'], 1)})

    data.sort(key=lambda x: x['_month'])
    for d in data:
        del d['_month']
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_stats(request):
    total_users = User.objects.filter(is_superuser=False).count()
    active_users = User.objects.filter(is_active=True, is_superuser=False).count()
    banned_users = UserProfile.objects.filter(is_banned=True).count()
    total_workouts = 45  # 9 workout categories x 5 exercises each
    return Response({
        'total_users': total_users,
        'active_users': active_users,
        'banned_users': banned_users,
        'total_workouts': total_workouts,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_users(request):
    users = User.objects.filter(is_superuser=False).select_related('userprofile').order_by('-date_joined')
    data = []
    for u in users:
        try:
            profile = u.userprofile
            is_banned = profile.is_banned
            weekly_score = profile.weekly_score
            name = profile.name or u.username
        except UserProfile.DoesNotExist:
            is_banned = False
            weekly_score = 0
            name = u.username
        data.append({
            'id': u.id,
            'name': name,
            'username': u.username,
            'email': u.email,
            'is_active': u.is_active,
            'is_banned': is_banned,
            'weekly_score': weekly_score,
            'joined': u.date_joined.strftime('%Y-%m-%d'),
            'status': 'banned' if is_banned else ('active' if u.is_active else 'inactive'),
        })
    return Response(data)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk, is_superuser=False)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    if request.method == 'DELETE':
        user.delete()
        return Response({'message': 'User deleted'})

    if request.method == 'PATCH':
        status_val = request.data.get('status')
        if status_val:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if status_val == 'banned':
                profile.is_banned = True
                user.is_active = False
            elif status_val == 'active':
                profile.is_banned = False
                user.is_active = True
            elif status_val == 'inactive':
                profile.is_banned = False
                user.is_active = False
            profile.save()
            user.save()
        return Response({'message': 'User updated'})