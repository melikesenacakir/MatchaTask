using Infra.Database;
using Core.Services.Abstract;
using Core.Entities;

namespace Infra.Repositories
{
    public class UsersRepository : Repository<User>, IUsersRepository
    {
        
        public UsersRepository(ApplicationDB db) : base(db)
        {
        }
    }
}