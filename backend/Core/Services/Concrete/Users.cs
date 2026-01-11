using Core.Services.Abstract;
namespace Core.Services.Concrete
{
    public class UserServices: IUsersService
    {
        private readonly IUsersRepository _usersRepo;
        public UserServices(IUsersRepository usersRepo)
        {
            _usersRepo = usersRepo;
        }
    }
}