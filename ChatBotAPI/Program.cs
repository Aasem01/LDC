using Microsoft.EntityFrameworkCore;
using ChatBotAPI.Data;
using Microsoft.OpenApi.Models;
using ChatBotAPI.Models;
using ChatBotAPI.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "ChatBot API", Version = "v1" });
});

// Configure Python Backend Settings
builder.Services.Configure<PythonBackendSettings>(
    builder.Configuration.GetSection("PythonBackend"));

// Configure HttpClient and Python Backend Service
builder.Services.AddHttpClient<IPythonBackendService, PythonBackendService>();

// Configure Database
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection")));

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "ChatBot API V1");
        c.RoutePrefix = "swagger";
    });
}

// Configure HTTPS
app.UseHttpsRedirection();
app.UseRouting();
app.UseAuthorization();
app.MapControllers();

app.Run();
